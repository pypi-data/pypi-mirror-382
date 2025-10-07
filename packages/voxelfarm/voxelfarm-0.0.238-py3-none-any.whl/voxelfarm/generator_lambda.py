import voxelfarm

class generator_lambda_framework:

    def __init__(self):  
       pass

    def input(self, id, label, default = 0.0):
        return 0.0

    def set_vector(self, index, vx, vy, vz):
        pass

    def set_material(self, index, id):
        pass

    def set_field(self, index, field):
        pass

    def set_entity_bounds(self, axis, v0, v1):
        pass

    def get_voxel_origin(self, index, dimension):
        return (0,0,0)

    def get_voxel_origin_axis(self, index, dimension, axis):
        return (0,0,0)

    def get_field_origin(self, index, dimension):
        return (0,0,0)

    def test(self):
        pass

class generator_lambda_host:

    version = (3,0,1,7)

    voxels = range(0, 44 * 44 * 44)
    field = range(0, 45 * 45 * 45)

    def __init__(self, framework = None):
        if framework:
            self.lambda_framework = framework
        else:
            if voxelfarm.voxelfarm_framework:
                self.lambda_framework = voxelfarm.voxelfarm_framework
            else:
                self.lambda_framework = generator_lambda_framework()

    def set_vector(self, index, vx, vy, vz):
        self.lambda_framework.set_vector(index, vx, vy, vz)

    def set_material(self, index, id):
        self.lambda_framework.set_material(index, id)

    def set_field(self, index, field):
        self.lambda_framework.set_field(index, field)

    def get_voxel_origin(self, index):
        return self.lambda_framework.get_voxel_origin(index, 44)

    def get_field_origin(self, index):
        return self.lambda_framework.get_voxel_origin(index, 45)

    def get_field_origin_x(self, index):
        return self.lambda_framework.get_voxel_origin_axis(index, 45, 0)

    def get_field_origin_y(self, index):
        return self.lambda_framework.get_voxel_origin_axis(index, 45, 1)

    def get_field_origin_z(self, index):
        return self.lambda_framework.get_voxel_origin_axis(index, 45, 2)

    def input(self, id, label, default = 0.0):
        return self.lambda_framework.input(id, label, default)

    def set_entity_bounds_x(self, v0, v1):
        if self.lambda_framework.set_entity_bounds(0, v0, v1) == 0:
            self.cellIsEmpty()

    def set_entity_bounds_y(self, v0, v1):
        if self.lambda_framework.set_entity_bounds(1, v0, v1) == 0:
            self.cellIsEmpty()

    def set_entity_bounds_z(self, v0, v1):
        if self.lambda_framework.set_entity_bounds(2, v0, v1) == 0:
            self.cellIsEmpty()

    def cellIsEmpty(self):
        self.voxels = range(0, 0)
        self.field = range(0, 0)

    def test(self):
        pass
