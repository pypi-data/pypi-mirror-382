from onescience.utils.openfold.geometry import rigid_matrix_vector
from onescience.utils.openfold.geometry import rotation_matrix
from onescience.utils.openfold.geometry import vector

Rot3Array = rotation_matrix.Rot3Array
Rigid3Array = rigid_matrix_vector.Rigid3Array

Vec3Array = vector.Vec3Array
square_euclidean_distance = vector.square_euclidean_distance
euclidean_distance = vector.euclidean_distance
dihedral_angle = vector.dihedral_angle
dot = vector.dot
cross = vector.cross
