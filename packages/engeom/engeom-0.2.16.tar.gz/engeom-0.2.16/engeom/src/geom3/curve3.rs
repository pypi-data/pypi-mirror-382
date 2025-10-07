use crate::common::Resample;
use crate::common::domain_window::DomainWindowIter;
use crate::common::points::{dist, ramer_douglas_peucker};
use crate::errors::InvalidGeometry;
use crate::geom3::{Iso3, Plane3, Point3, UnitVec3};
use crate::{Func1, Polynomial, Result, Smoothing, SurfacePoint3, SvdBasis3};
use parry3d_f64::na::Unit;
use parry3d_f64::query::PointQueryWithLocation;
use parry3d_f64::shape::Polyline;

#[derive(Copy, Clone)]
pub struct CurveStation3<'a> {
    point: Point3,

    direction: UnitVec3,

    index: usize,

    fraction: f64,

    curve: &'a Curve3,
}

impl<'a> CurveStation3<'a> {
    fn new(
        point: Point3,
        direction: UnitVec3,
        index: usize,
        fraction: f64,
        curve: &'a Curve3,
    ) -> Self {
        Self {
            point,
            direction,
            index,
            fraction,
            curve,
        }
    }

    pub fn point(&self) -> Point3 {
        self.point
    }

    pub fn direction(&self) -> UnitVec3 {
        self.direction
    }

    /// Returns a SurfacePoint3 at the same position in 3d space as the station, but with a normal
    /// pointing in the direction of the next vertex on the curve.
    pub fn direction_point(&self) -> SurfacePoint3 {
        SurfacePoint3::new(self.point, self.direction)
    }

    pub fn index(&self) -> usize {
        self.index
    }

    pub fn fraction(&self) -> f64 {
        self.fraction
    }

    pub fn curve(&self) -> &'a Curve3 {
        self.curve
    }

    pub fn at_index(&self) -> Self {
        self.curve.at_vertex(self.index)
    }

    pub fn length_along(&self) -> f64 {
        let l = self.curve.lengths();
        l[self.index] + (l[self.index + 1] - l[self.index]) * self.fraction
    }

    pub fn plane(&self) -> Plane3 {
        Plane3::from((&self.direction, &self.point))
    }

    pub fn is_front(&self) -> bool {
        self.length_along() < self.curve.tol
    }

    pub fn is_back(&self) -> bool {
        self.length_along() > self.curve.length() - self.curve.tol
    }
}

#[derive(Clone)]
pub struct Curve3 {
    line: Polyline,
    lengths: Vec<f64>,
    tol: f64,
}

impl Curve3 {
    pub fn vtx(&self, i: usize) -> Point3 {
        self.line.vertices()[i]
    }

    pub fn points(&self) -> &[Point3] {
        self.line.vertices()
    }

    pub fn transformed_by(&self, iso: &Iso3) -> Self {
        let points = self
            .line
            .vertices()
            .iter()
            .map(|p| iso * p)
            .collect::<Vec<_>>();
        Self::from_points(&points, self.tol).unwrap()
    }

    pub fn from_points(points: &[Point3], tol: f64) -> Result<Self> {
        let mut points = points.to_vec();
        points.dedup_by(|a, b| dist(a, b) <= tol);
        if points.len() < 2 {
            return Err(Box::from(InvalidGeometry::NotEnoughPoints));
        }

        let line = Polyline::new(points, None);
        let v = line.vertices();

        let mut lengths = vec![0.0];
        for i in 0..v.len() - 1 {
            let d = dist(&v[i + 1], &v[i]);
            lengths.push(lengths[i] + d);
        }

        Ok(Self { line, lengths, tol })
    }

    pub fn count(&self) -> usize {
        self.line.vertices().len()
    }

    pub fn lengths(&self) -> &[f64] {
        &self.lengths
    }

    pub fn length(&self) -> f64 {
        *self.lengths.last().unwrap()
    }

    fn dir_of_edge(&self, edge_index: usize) -> UnitVec3 {
        Unit::new_normalize(self.vtx(edge_index + 1) - self.vtx(edge_index))
    }

    fn dir_of_vertex(&self, index: usize) -> UnitVec3 {
        if index == self.line.vertices().len() - 1 {
            self.dir_of_edge(index - 1)
        } else {
            self.dir_of_edge(index)
        }
    }

    fn at_vertex(&self, index: usize) -> CurveStation3<'_> {
        let (i, f) = if index == self.line.vertices().len() - 1 {
            (index - 1, 1.0)
        } else {
            (index, 0.0)
        };

        CurveStation3::new(
            self.line.vertices()[index],
            self.dir_of_vertex(index),
            i,
            f,
            self,
        )
    }

    pub fn at_length(&self, length: f64) -> Option<CurveStation3<'_>> {
        if length < 0.0 || length > self.length() {
            None
        } else {
            let search = self
                .lengths
                .binary_search_by(|l| l.partial_cmp(&length).unwrap());
            match search {
                Ok(index) => Some(self.at_vertex(index)),
                Err(next_index) => {
                    let index = next_index - 1;
                    let dir = self.dir_of_edge(index);
                    let remaining = length - self.lengths[index];
                    let f = remaining / (self.lengths[index + 1] - self.lengths[index]);
                    let point = self.vtx(index) + dir.into_inner() * remaining;
                    Some(CurveStation3::new(point, dir, index, f, self))
                }
            }
        }
    }

    pub fn at_fraction(&self, fraction: f64) -> Option<CurveStation3<'_>> {
        self.at_length(fraction * self.length())
    }

    pub fn at_closest_to_point(&self, test_point: &Point3) -> CurveStation3<'_> {
        let (prj, loc) = self
            .line
            .project_local_point_and_get_location(test_point, false);
        let (edge_index, sp) = loc;
        CurveStation3::new(
            prj.point,
            self.dir_of_edge(edge_index as usize),
            edge_index as usize,
            sp.barycentric_coordinates()[1],
            self,
        )
    }

    pub fn resample(&self, mode: Resample) -> Self {
        match mode {
            Resample::ByCount(n) => resample_by_count(self, n),
            Resample::BySpacing(l) => resample_by_spacing(self, l),
            Resample::ByMaxSpacing(lm) => resample_by_max_spacing(self, lm),
        }
    }

    pub fn dist_to_point(&self, test_point: &Point3) -> f64 {
        let (prj, _) = self
            .line
            .project_local_point_and_get_location(test_point, false);
        dist(test_point, &prj.point)
    }

    pub fn tol(&self) -> f64 {
        self.tol
    }

    pub fn vertices(&self) -> &[Point3] {
        self.line.vertices()
    }

    pub fn clone_points(&self) -> Vec<Point3> {
        self.line.vertices().to_vec()
    }

    pub fn at_front(&self) -> CurveStation3<'_> {
        self.at_vertex(0)
    }

    pub fn at_back(&self) -> CurveStation3<'_> {
        self.at_vertex(self.line.vertices().len() - 1)
    }

    pub fn iter(&self) -> Curve3Iterator<'_> {
        Curve3Iterator {
            curve: self,
            index: 0,
        }
    }

    pub fn simplify(&self, tol: f64) -> Self {
        let new_points = ramer_douglas_peucker(self.line.vertices(), tol);
        Self::from_points(&new_points, tol).unwrap()
    }

    pub fn smoothed(&self, mode: Smoothing) -> Result<Self> {
        match mode {
            Smoothing::Gaussian(_sigma) => {
                todo!()
            }
            Smoothing::Quadratic(window) => smooth_by_polynomial::<3>(self, window),
            Smoothing::Cubic(window) => smooth_by_polynomial::<4>(self, window),
        }
    }

    pub fn window_iter(&self, window_size: f64) -> DomainWindowIter<'_> {
        DomainWindowIter::new(self.lengths(), window_size)
    }
}

fn smooth_by_polynomial<const D: usize>(curve: &Curve3, window_size: f64) -> Result<Curve3> {
    let mut new_points = Vec::new();
    for window in curve.window_iter(window_size) {
        let points = window
            .iter()
            .map(|i| curve.line.vertices()[i])
            .collect::<Vec<_>>();

        if points.len() < 3 {
            new_points.push(curve.line.vertices()[window.index]);
            continue;
        }

        let svd = SvdBasis3::from_points(&points, None).ok_or("Failed to compute SVD basis")?;
        let svd_t = Iso3::from(&svd);

        let mut xs = Vec::new();
        let mut ys = Vec::new();
        for p in &points {
            let pt = svd_t * p;
            xs.push(pt.x);
            ys.push(pt.y);
        }

        let Some(poly) = Polynomial::<D>::least_squares(&xs, &ys, None) else {
            return Err("Failed to fit polynomial".into());
        };

        let x = (svd_t * curve.line.vertices()[window.index]).x;
        let y = poly.f(x);
        new_points.push(svd_t.inverse() * Point3::new(x, y, 0.0));
    }

    Curve3::from_points(&new_points, curve.tol())
}

fn resample_by_max_spacing(curve: &Curve3, max_spacing: f64) -> Curve3 {
    // Find the number of points it will take to ensure that the spacing is less than the max
    // spacing
    let n = (curve.length() / max_spacing).ceil() as usize;
    resample_by_count(curve, n)
}

fn resample_by_spacing(curve: &Curve3, spacing: f64) -> Curve3 {
    let mut positions = Vec::new();
    let mut length = 0.0;
    while length < curve.length() {
        positions.push(length);
        length += spacing;
    }

    // Center
    let padding = (curve.length() - positions.last().unwrap()) / 2.0;
    for p in &mut positions {
        *p += padding;
    }

    resample_at_positions(curve, &positions)
}

fn resample_by_count(curve: &Curve3, n: usize) -> Curve3 {
    let mut positions = Vec::new();
    for i in 0..n {
        let f = i as f64 / (n - 1) as f64;
        positions.push(f * curve.length());
    }

    resample_at_positions(curve, &positions)
}

fn resample_at_positions(curve: &Curve3, positions: &[f64]) -> Curve3 {
    let mut points = Vec::new();
    for p in positions {
        let station = curve.at_length(*p).unwrap();
        points.push(station.point());
    }
    Curve3::from_points(&points, curve.tol()).unwrap()
}

pub struct Curve3Iterator<'a> {
    curve: &'a Curve3,
    index: usize,
}

impl<'a> Iterator for Curve3Iterator<'a> {
    type Item = CurveStation3<'a>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.index < self.curve.line.vertices().len() {
            let result = self.curve.at_vertex(self.index);
            self.index += 1;
            Some(result)
        } else {
            None
        }
    }
}
