# %%
import numpy as np
import open3d as o3d
import torch
import trimesh
from skimage.measure import marching_cubes

from lib.models.deepsdf import DeepSDF
from lib.utils import load_config

cfg = load_config()
npy_path = f"{cfg['data_path']}/03001627/3c4ed9c8f76c7a5ef51f77a6d7299806/points.npy"
N = 4
checkpoint_path = "/home/korth/sketch2shape/checkpoint/deepsdf/shapenet_chair_single-epoch=49-train/loss=0.00.ckpt"
deepsdf = DeepSDF.load_from_checkpoint(checkpoint_path)

grid_vals = torch.arange(-1, 1, float(1 / N))
grid = torch.meshgrid(grid_vals, grid_vals, grid_vals)

xyz = (
    torch.stack((grid[0].ravel(), grid[1].ravel(), grid[2].ravel()))
    .reshape(-1, 3)
    .to(torch.float64)
)

lat_vec = torch.zeros(xyz.shape[0]).int()
lat_vec = deepsdf.lat_vecs(lat_vec)
x = (xyz, lat_vec)
sd = deepsdf.predict(xyz, lat_vec)
sd = sd.reshape(2 * N, 2 * N, 2 * N).detach().numpy()

verts, faces, normals, values = marching_cubes(sd, level=0.0)

x_max = np.array([1, 1, 1])
x_min = np.array([-1, -1, -1])
verts = verts * ((x_max - x_min) / (2 * N)) + x_min
# mesh = o3d.geometry.TriangleMesh()
# mesh.vertices = o3d.utility.Vector3dVector(verts)
# mesh.triangles = o3d.utility.Vector3dVector(faces)
# o3d.io.write_triangle_mesh(f"{cfg['data_path']}/test.obj", mesh)
trimesh.exchange.export.export_mesh(
    trimesh.Trimesh(verts, faces), f"{cfg['data_path']}/test1.obj", file_type="obj"
)
# %%
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Display resulting triangular mesh using Matplotlib. This can also be done
# with mayavi (see skimage.measure.marching_cubes docstring).
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection="3d")

# Fancy indexing: `verts[faces]` to generate a collection of triangles
mesh = Poly3DCollection(verts[faces])
mesh.set_edgecolor("k")
ax.add_collection3d(mesh)

ax.set_xlabel("x-axis: a = 6 per ellipsoid")
ax.set_ylabel("y-axis: b = 10")
ax.set_zlabel("z-axis: c = 16")

ax.set_xlim(0, 24)  # a = 6 (times two for 2nd ellipsoid)
ax.set_ylim(0, 20)  # b = 10
ax.set_zlim(0, 32)  # c = 16

plt.tight_layout()
plt.show()

# %%
