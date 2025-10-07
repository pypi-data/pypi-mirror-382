import json

import rhino3dm
from rhino3dm import Vector3d, Mesh
from rhino3dm import File3dm
from rhino3dm import Point3f,Point3d

from ladybug_geometry.geometry3d import Point3D,Mesh3D

def vector3d_from_str(vector:tuple) -> Vector3d:
    return Vector3d(vector[0], vector[1], vector[2])


def mesh_from_3dm(json:dict) -> Mesh|None:

    return None

def rmesh_to_lmesh(mesh:Mesh) ->Mesh3D:
    _mesh = Mesh3D(rpointf_to_lpoint(mesh.Vertices), mesh.Faces)

    return _mesh

def lmesh_to_rmesh(mesh:Mesh3D) ->Mesh:
    _mesh=Mesh()
    try:
        vertices=mesh.vertices
    except:
        return _mesh
    for v in vertices:
        _mesh.Vertices.Add(v.x,v.y,v.z)
    face=mesh.faces
    for f in face:
        if len(f)==4:
            _mesh.Faces.AddFace(f[0],f[1],f[2],f[3])
        else:
            _mesh.Faces.AddFace(f[0], f[1], f[2])

    return _mesh

def lmeshs_to_rmeshs(mesh:[Mesh3D]) ->[Mesh]:
    _mesh=[]
    for m in mesh:
        _m=lmesh_to_rmesh(m)
        _mesh.append(_m)
    return _mesh

def rpointf_to_lpoint(points:[Point3f]) -> [Point3D]:

    result=[]
    for p in points:
        result.append(Point3D(p.X, p.Y, p.Z))

    return result

def lpointf_to_rpoint(points:[Point3D]) -> [Point3d]:

    result=[]
    for p in points:
        result.append(Point3d(p.X, p.Y, p.Z))

    return result



def read3dm(file_bytes:bytes) ->dict[str,list|dict]:
    file = rhino3dm._rhino3dm.File3dm.FromByteArray(file_bytes)
    objectstable = file.Objects
    geometry={}
    for obj in objectstable:
        if obj.Attributes.Name=="jsondata":
            a=obj.Attributes.GetUserStrings()
            geometry['jsondata']=json.loads(a[0][1])
        else:
            _geolist=geometry.setdefault(obj.Attributes.Name,[])

            _geolist.append(obj.Geometry)
    return geometry

def write3dm(geometry:dict,oterdata=None)->File3dm:
    file3dm=File3dm()
    objecttable=file3dm.Objects
    for k,g in geometry.items():
        attribute=rhino3dm.ObjectAttributes()
        #attribute.Name=k
        objecttable.Add(g)

    if oterdata!=None:
        attribute = rhino3dm.ObjectAttributes()
        attribute.SetUserString("jsondata",json.dumps(oterdata))
        _p=file3dm.Objects.AddPoint(0,0,0,attribute)

    return file3dm
