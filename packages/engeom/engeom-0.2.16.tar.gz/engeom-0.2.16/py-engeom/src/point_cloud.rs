use crate::conversions::{array_to_points3, points_to_array, vectors_to_array};
use crate::geom3::Iso3;
use crate::mesh::Mesh;
use engeom::{PointCloudFeatures, PointCloudKdTree, PointCloudOverlap};
use numpy::ndarray::Array2;
use numpy::{IntoPyArray, PyArray2, PyReadonlyArray2};
use pyo3::exceptions::{PyIOError, PyValueError};
use pyo3::prelude::*;
use std::path::PathBuf;

#[pyclass]
#[derive(Clone, Copy, Debug)]
pub enum Lptf3Load {
    All {},
    TakeEveryN {
        n: u32,
    },
    SmoothSample {
        take_every: u32,
        look_scale: f64,
        weight_scale: f64,
        max_move: f64,
    },
}

#[pymethods]
impl Lptf3Load {
    fn __repr__(&self) -> String {
        match self {
            Lptf3Load::All {} => "Lptf3Load.All".to_string(),
            Lptf3Load::TakeEveryN { n } => format!("Lptf3Load.TakeEveryN({})", n),
            Lptf3Load::SmoothSample {
                take_every,
                look_scale,
                weight_scale,
                max_move,
            } => format!(
                "Lptf3Load.SmoothSample(take_every={}, look_scale={}, weight_scale={}, max_move={})",
                take_every, look_scale, weight_scale, max_move
            ),
        }
    }
}

impl From<Lptf3Load> for engeom::io::Lptf3Load {
    fn from(load: Lptf3Load) -> Self {
        match load {
            Lptf3Load::All {} => engeom::io::Lptf3Load::All,
            Lptf3Load::TakeEveryN { n } => engeom::io::Lptf3Load::TakeEveryN(n),
            Lptf3Load::SmoothSample {
                take_every,
                look_scale,
                weight_scale,
                max_move,
            } => {
                let p =
                    engeom::io::Lptf3DsParams::new(take_every, look_scale, weight_scale, max_move);
                engeom::io::Lptf3Load::SmoothSample(p)
            }
        }
    }
}

#[pyclass]
pub struct PointCloud {
    inner: engeom::PointCloud,
    points: Option<Py<PyArray2<f64>>>,
    normals: Option<Py<PyArray2<f64>>>,
    colors: Option<Py<PyArray2<u8>>>,
    matched_tree: Option<engeom::common::kd_tree::MatchedTree<3>>,
}

impl PointCloud {
    fn clear_cached(&mut self) {
        self.points = None;
        self.normals = None;
        self.colors = None;
        self.matched_tree = None;
    }

    pub fn get_inner(&self) -> &engeom::PointCloud {
        &self.inner
    }

    pub fn from_inner(inner: engeom::PointCloud) -> Self {
        Self {
            inner,
            points: None,
            normals: None,
            colors: None,
            matched_tree: None,
        }
    }

    pub fn with_tree(&mut self) -> PyResult<PointCloudKdTree<'_>> {
        if self.matched_tree.is_none() {
            let tree = self
                .inner
                .create_matched_tree()
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
            self.matched_tree = Some(tree);
        }

        let tree = self.matched_tree.as_ref().unwrap();
        PointCloudKdTree::try_new(&self.inner, tree)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }
}

impl Clone for PointCloud {
    fn clone(&self) -> Self {
        Self::from_inner(self.inner.clone())
    }
}

#[pymethods]
impl PointCloud {
    #[new]
    fn new<'py>(points: PyReadonlyArray2<'py, f64>) -> PyResult<Self> {
        let cloud_points = array_to_points3(&points.as_array())?;
        let cloud = engeom::PointCloud::try_new(cloud_points, None, None, None)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        Ok(Self::from_inner(cloud))
    }

    #[staticmethod]
    fn load_lptf3(path: PathBuf, params: Lptf3Load) -> PyResult<Self> {
        let inner = engeom::io::load_lptf3(&path, params.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))?;
        Ok(Self::from_inner(inner))
    }

    #[staticmethod]
    fn load_bxyz(path: PathBuf) -> PyResult<Self> {
        let inner = engeom::io::load_bxyz(&path).map_err(|e| PyIOError::new_err(e.to_string()))?;
        Ok(Self::from_inner(inner))
    }

    fn cloned(&self) -> Self {
        self.clone()
    }

    fn append(&mut self, other: &PointCloud) -> PyResult<()> {
        self.clear_cached();
        let clone = other.inner.clone();
        self.inner
            .merge(clone)
            .map_err(|e| PyValueError::new_err(e.to_string()))
    }

    #[getter]
    fn points<'py>(&mut self, py: Python<'py>) -> &Bound<'py, PyArray2<f64>> {
        if self.points.is_none() {
            let array = points_to_array(self.inner.points());
            self.points = Some(array.into_pyarray(py).unbind());
        }
        self.points.as_ref().unwrap().bind(py)
    }

    #[getter]
    fn colors<'py>(&mut self, py: Python<'py>) -> Option<&Bound<'py, PyArray2<u8>>> {
        if let Some(colors) = self.inner.colors() {
            if self.colors.is_none() {
                let flat_colors = colors.iter().flatten().copied().collect::<Vec<_>>();
                let array = Array2::from_shape_vec((self.inner.points().len(), 3), flat_colors)
                    .expect("Failed to create color array");
                self.colors = Some(array.into_pyarray(py).unbind());
            }

            Some(self.colors.as_ref().unwrap().bind(py))
        } else {
            None
        }
    }

    #[getter]
    fn normals<'py>(&mut self, py: Python<'py>) -> Option<&Bound<'py, PyArray2<f64>>> {
        if let Some(normals) = self.inner.normals() {
            if self.normals.is_none() {
                let n = normals.iter().map(|v| v.into_inner()).collect::<Vec<_>>();
                let array = vectors_to_array(&n);
                self.normals = Some(array.into_pyarray(py).unbind());
            }

            Some(self.normals.as_ref().unwrap().bind(py))
        } else {
            None
        }
    }

    fn transform_by(&mut self, transform: &Iso3) {
        self.clear_cached();
        self.inner.transform_by(transform.get_inner());
    }

    fn create_from_indices(&self, indices: Vec<usize>) -> PyResult<Self> {
        let inner = self
            .inner
            .create_from_indices(&indices)
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        Ok(Self::from_inner(inner))
    }

    fn sample_poisson_disk(&mut self, radius: f64) -> PyResult<Vec<usize>> {
        let with_tree = self
            .with_tree()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        let mask = with_tree.sample_poisson_disk(radius);

        Ok(mask.to_indices())
    }

    fn create_from_poisson_sample(&mut self, radius: f64) -> PyResult<Self> {
        let with_tree = self
            .with_tree()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        with_tree
            .create_from_poisson_sample(radius)
            .map_err(|e| PyValueError::new_err(e.to_string()))
            .map(Self::from_inner)
    }

    fn overlap_points_by_reciprocity(
        &mut self,
        other: &mut PointCloud,
        max_distance: f64,
    ) -> PyResult<Vec<usize>> {
        let this_with_tree = self
            .with_tree()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        let other_with_tree = other
            .with_tree()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        Ok(this_with_tree.overlap_by_reciprocity(&other_with_tree, max_distance))
    }

    fn overlap_mesh_by_reciprocity(
        &mut self,
        mesh: &Mesh,
        max_distance: f64,
    ) -> PyResult<Vec<usize>> {
        let this_with_tree = self
            .with_tree()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;

        Ok(this_with_tree.overlap_by_reciprocity(mesh.get_inner(), max_distance))
    }
}
