from ladybug_geometry.geometry3d import Mesh3D,Face3D,Ray3D,Plane,Polyline3D,Vector3D,Point3D,Sphere
from ladybug_geometry.intersection3d import intersect_line3d_plane
from ladybug_geometry.geometry2d import Polygon2D
from ladybug.sunpath import Sunpath,Sun



from ladybug_geometry.projection import project_geometry
from ladybug_geometry.bounding import bounding_box
from ladybug_geometry.bounding import bounding_rectangle



from ladybug.epw import EPW
from rhino3dm import PointCloud

import math

from sunanalysis.util import *
from ladybug_geometry import bounding

def intersect_line3d_mesh(ray:Ray3D,mesh:Mesh3D)->tuple[Point3D|None,int|None]:
    l_mesh_faces_normals=mesh.face_normals
    l_mesh_faces_centers = mesh.face_centroids
    planes=[]
    for n,c in zip(l_mesh_faces_normals,l_mesh_faces_centers):
        _p=Plane(n,c)
        planes.append(_p)

    for index, p in enumerate(planes):
        inter=intersect_line3d_plane(ray,p)
        if inter!=None:
            return inter,index
    return None,None

def intersect_line3d_planermesh(ray:Ray3D,pointcloud:PointCloud,plane,tolance=1000)->tuple[Point3D|None,int|None]:

    inter=intersect_line3d_plane(ray,plane)
    if inter==None:
        return None,None
    else:
        _i=pointcloud.ClosestPoint(Point3d(inter.x,inter.y,inter.z))
        p=pointcloud.PointAt(_i)
        distance=p.DistanceTo(Point3d(inter.x,inter.y,inter.z))
        if distance>tolance:
            return None,None
        return inter, _i


"""
class ReflectOnGround(object):
    def __init__(self,reflect_rec:[Polyline],reflectvector:[[Vector3d]],reflect_value,mesh:Mesh,curtain_wall:Mesh):
        self.reflect_rec = reflect_rec
        self.reflectvector = pd.DataFrame(reflectvector)
        self.reflect_value = reflect_value
        self.mesh = mesh
        self.is_include=True
        self.curtain_wall = curtain_wall

    def Cells(self)->[int]:
        return None
    def rayOnMesh(self,rec:Polyline, vector:Vector3d, mesh:Mesh):
        Line=[]
        ps = [p for p in rec]
        ps.pop(-1)
        # reflected corner in ground
        newp = []
        lmesh=rmesh_to_lmesh(mesh)

        for p in ps:
            ray = Ray3D(p,vector)

            p,index = intersect_line3d_mesh(ray,lmesh)
            if p==None:
                pass
            else:
                newp.append(p)

        if len(newp) < 3:
            return []
        newp.append(newp[0])
        # create polygone on ground
        poly =Polyline3D(newp).to_polyline2d().to_polygon(1)
        Line.append(poly)
        # find mesh index in projected poly
        meshcenters=lmesh.face_centroids
        indexs=[]
        for index, p in enumerate(meshcenters):
            result=poly.point_relationship(p,1)
            if result==1:
                indexs.append(index)
        return indexs


    def raysOnMesh(self,rays):
        # reflect rays per time. rays from differnt glass panel
        rendervalue=[{i:0} for i in range(0,self.mesh.Faces.Count)]
        for index, r in enumerate(rays):
            index = self.rayOnMesh(self.reflect_rec[index], r, self.mesh)
            for _i in index:
                rendervalue[_i] += 1
                # create append cell
                #Cells[_i].reflect_vector.append(r)

        return rendervalue
    def run(self):
        for i in self.reflectvector:
            if self.is_include:
                iu = self.reflect_value[i]
                if iu > 4000:
                    self.raysOnMesh(self.reflectvector[i])
            else:
                self.raysOnMesh(self.reflectvector[i])

"""
class GlareReflectionArea(object):
    def __init__(self,mesh:Mesh,input_vectors):
        self.mesh = mesh
        self.mesh_normals=mesh.Normals
        self.mesh_vertices=mesh.Vertices
        self.mesh_faces=mesh.Faces
        self.input_vectors = input_vectors
    def Cells(self)->[int]:
        return None

    def reflect_rec(self):
        _mesh=Mesh3D(rpointf_to_lpoint(self.mesh_vertices),self.mesh_faces)
        edges=_mesh.edges

        print(edges)



        return _mesh
    def reflect_vectors(self):

        return None


class AshraeSky():
    """
    室外照度模型
    """
    def __init__(self,latitude:float,reflection:float,h:[]):
        self.latitude=latitude
        #reflection is 反射率
        self.reflection=reflection
        self.h=h
    @staticmethod
    def EE(h, A=1.37):
        if h > 0:  # 太阳在地平线上
            try:
                _E = (A * 10 ** 5) * math.exp(-0.223 / math.sin(math.radians(h)))
            except:
                _E = 0
        else:
            _E = 0

        return _E
    @staticmethod
    def liangdu(fanshe, E):
        return fanshe * E / math.pi
    def luxvalue(self)->[float]:
        """
        return lux value by h
        :return:
        """
        lux_value=[]
        result=[]
        for _h in self.h:
            _E = self.EE(_h)
            lux_value.append(_E)
            _result = self.liangdu(self.reflection, _E)
            result.append(_result)
        return  result

class CalResult():
    """
    Stu to save Reflection result. Store analysied face and panel face paires.
    """
    def __init__(self,mesh:Mesh3D|None,glassindex:int,analysismeshindex:list[int],analysismeshindex2:list[int],sunindex:int):
        self.m=mesh
        #self.ismid=ismid
        #self.overlay=overlay
        self.glassindex=glassindex
        self.analysismeshindex=analysismeshindex
        self.analysismeshindex2=analysismeshindex2
        self.sunindex=sunindex
class SunTranceResult():
    """
    Stu to save Reflection result. Store analysied face and panel face paires.
    """
    def __init__(self,sunreflectray:Mesh3D|bool|None,glassindex:int|None,analysismeshindex:int|None,sunindex:int,isblocked:bool=False,lux:float=0):
        self.m=sunreflectray
        self.glassindex=glassindex
        self.analysismeshindex=analysismeshindex
        self.sunindex=sunindex
        self.isblocked=isblocked
        self.lux=lux

class Obstaclemesh():
    def __init__(self,mesh:Mesh3D):
        self.mesh=mesh
        self.boundingsphere=self._boundingsphere()
        self. face3ds = self._face3ds()

    def _boundingsphere(self)->Sphere:
        center = self.mesh.center
        maxp = self.mesh.max
        distance = center.distance_to_point(maxp)
        sp = Sphere(center, distance)
        return sp
    def _face3ds(self)->list[Face3D]:
        return [Face3D(i) for i in self.mesh.face_edges]


class CalReflection():
    """
    glass and input_vector one vs one
    """
    def __init__(self,glassface:Face3D,glassindex:int,sun:Sun,sunindex:int,latitude:float,obstaclemesh:list[Obstaclemesh],glassreflection:float=0.10,returnmesh=False):
        self.glassface=glassface
        self.input_vecotr=sun.sun_vector
        self.sun=sun
        self.sunindex=sunindex
        self.glassindex=glassindex
        self.latitude=latitude
        self.glassreflection=glassreflection
        self.obstaclemesh=obstaclemesh
        self.returnmesh=returnmesh
    @property
    def input_ray(self)->Ray3D:
        glassmidpoint = self.glassface.centroid
        input_ray = Ray3D(glassmidpoint, self.sun.sun_vector)
        return input_ray
    def sunisabove(self):
        """
        to test is sun point in the side of reflection
        :return:
        """
        plane=self.glassface.plane
        center=self.glassface.centroid

        inputray=self.input_ray

        sunpoint=center.move(inputray.v*-1000)
        if plane.is_point_above(sunpoint):
            return True
        else:
            return False
    def filertsun(self,max=4000):
        """
        test sun lunmiance value
        :return:
        """
        sky=AshraeSky(self.latitude,self.glassreflection,[self.sun.altitude])
        glarevalue=sky.luxvalue()[0]
        #print(glarevalue)
        if glarevalue > max:
            return True
        else:
            return False
    def reflectlux(self):
        """
        test sun lunmiance value
        :return:
        """
        sky=AshraeSky(self.latitude,self.glassreflection,[self.sun.altitude])
        glarevalue=sky.luxvalue()[0]
        return glarevalue
    def issunblocked(self)->bool:
        """
        test sun blocked  ,if blocked return true else return false
        :return:
        """
        refelct_ray,input_ray = self.reflect_ray()
        leftmeshs=[]
        for om in self.obstaclemesh:

            inter=om.boundingsphere.intersect_line_ray(input_ray.reverse())
            inter2 = om.boundingsphere.intersect_line_ray(refelct_ray)
            if inter!=None or inter2!=None:
                leftmeshs.append(om)

        for obstaclemesh in leftmeshs:
            face3d =obstaclemesh.face3ds
            for f in face3d:
                isintersect=f.intersect_line_ray(input_ray.reverse())
                isintersect2 = f.intersect_line_ray(refelct_ray)
                if isintersect!=None or isintersect2!=None:
                    return True
        return False

    def input_rays(self)->[Ray3D]:
        """
        get input ray for each glass panel corner
        :return:
        """
        ps=self.glassface.vertices
        rays=[Ray3D(p,self.input_vecotr) for p in ps]
        return rays
    def reflect_rays(self)->[Ray3D]:
        """
        get reflect ray for each glass panel corner
        :return:
        """
        plane=self.glassface.plane
        ps=self.glassface.vertices
        input_rays=self.input_rays()
        reflect_rays=[]
        for index, ray in enumerate(input_rays):
            _ray=ray.reflect(plane.n,ps[index])
            reflect_rays.append(_ray)
        return reflect_rays
    def reflect_ray(self)->tuple[Ray3D,Ray3D]:
        """
        get reflect ray for each glass panel center
        :return:
        """
        plane=self.glassface.plane
        ps_center=self.glassface.center
        input_ray=self.input_ray

        _ray=input_ray.reflect(plane.n,ps_center)

        return _ray,input_ray
    @staticmethod
    def testresult(projectpolygon:Polygon2D,analysisedpolygon:Polygon2D):

        center=analysisedpolygon.center
        includemid=projectpolygon.is_point_inside(center)
        _overlap = projectpolygon.polygon_relationship(analysisedpolygon, 1)
        return includemid , _overlap!=-1

    def reflect_polyone(self,analysismesh:Mesh3D)->CalResult:
        """
        glass panel reflect to the analysismesh and save the result of cal
        :param analysismesh:
        :return:
        """
        # exclude the ray not reach the lux min,and ray at the backside of panel
        if self.filertsun()!=True or self.sunisabove()!=False or self.issunblocked()==True:
            return CalResult(None,self.glassindex,[],[],self.sunindex)
        #get all reflect rays
        reflect_rays=self.reflect_rays()
        plane=Face3D(analysismesh.face_edges[0]).plane

        ps=[plane.intersect_line_ray(r) for r in reflect_rays]
        # if any point can not project to analysied mesh,return
        if None in ps:
            return CalResult(None,self.glassindex,[],[],self.sunindex)
        else:
            polyline=Polyline3D(ps)
            polyline2d=polyline.to_polyline2d().to_polygon(1)

            index=[]
            _index=[]
            #test if analysised center inside project polygon
            for _i,f in enumerate(analysismesh.face_edges):
                _f2d=f.to_polyline2d().to_polygon(1)

                ismid,_overlap=self.testresult(polyline2d,_f2d)
                if ismid:
                    _index.append(_i)
                if _overlap:
                    index.append(_i)
            _m = Mesh3D(polyline.vertices, [(0, 1, 2, 3)])
            return CalResult(_m,self.glassindex,_index,index,self.sunindex)

    def ishitanalysis(self,pointcloud,plane,tol=1500):
        centerpointcloud=PointCloud.Decode(pointcloud)
        reflect_ray,input_ray=self.reflect_ray()
        return intersect_line3d_planermesh(reflect_ray,centerpointcloud,plane,tolance=tol)


    def sunraytrance_polyline(self,pointcloud:dict,plane:Plane,tol=1500)->SunTranceResult:
        """
        glass panel reflect to the analysismesh and save the result of cal
        :param analysismesh:
        :return:
        """
        #cetners=analysismesh.face_area_centroids
        #centerpointcloud=PointCloud()
        #for c in cetners:
            #centerpointcloud.Add(Point3d(c.x,c.y,c.z))

        #print(self.issunblocked())
        # exclude the ray not reach the lux min,and ray at the backside of panel
        if self.sunisabove()==False or self.filertsun()!=True:
            return SunTranceResult(None,self.glassindex,None,self.sunindex,lux=self.reflectlux())
        #get all reflect rays




        # if any point can not project to analysied mesh,return
        if self.issunblocked()==True:
            return SunTranceResult(None,self.glassindex,None,self.sunindex,isblocked=True,lux=self.reflectlux())

            #_pl = Polyline3D([self.sun.position_3d(),self.glassface.center, interp])

        #centerpointcloud=PointCloud.Decode(pointcloud)
        #reflect_ray,input_ray=self.reflect_ray()
        interp,interindex=self.ishitanalysis(pointcloud,plane,tol=tol)
        if interp==None:
            return SunTranceResult(None, self.glassindex, None, self.sunindex,lux=self.reflectlux())
        if self.returnmesh:
            _sp=self.glassface.center.move(self.input_ray.v*-5000)


            _m=Mesh3D([_sp,self.glassface.center, interp], [(0, 1, 2)])

            return SunTranceResult(_m,self.glassindex,interindex,self.sunindex,lux=self.reflectlux())
        else:
            return SunTranceResult(True, self.glassindex, interindex, self.sunindex,lux=self.reflectlux())

class Glare_Analysis():
    def __init__(self,epwpath:str, hoys:list[int],building:Mesh3D,analysisgird:Mesh3D,selectedindex:[]):
        self.epw=EPW(epwpath)
        self.hoys=hoys
        self.building=building
        self.analyaisgird=analysisgird
        self.selectedindex=selectedindex
        self.sunpath=Sunpath(self.epw.location.latitude,self.epw.location.longitude,self.epw.location.time_zone)
    @property
    def analysisgirdtopointcloud(self)->dict:

        pc=PointCloud()
        for p in self.analyaisgird.face_centroids:
            pc.Add(Point3d(p.x,p.y,p.z))
        return pc.Encode()
    @property
    def analysisplane(self)->Plane:
        noraml=self.analyaisgird.face_normals
        ceter=self.analyaisgird.face_centroids
        return Plane(noraml[0],ceter[0])
    def sun(self)->[Sun]:
        """
        get sun by hoys
        :return:
        """
        sun=[self.sunpath.calculate_sun_from_hoy(h) for h in self.hoys]
        return sun
    def luxvalues(self)->[float]:
        """
        get lux value
        :return:
        """
        ashrae=AshraeSky(self.epw.location.latitude,0.10,[s.altitude for s in self.sun()])

        return ashrae.luxvalue()
    def luxvalue(self,index)->float:
        """
        get lux value
        :return:
        """
        ashrae=AshraeSky(self.epw.location.latitude,0.10,[s.altitude for s in self.sun()[index]])

        return ashrae.luxvalue()[0]

    @staticmethod
    def plane_reflect(p:Plane,v:Vector3D)->Ray3D:
        ray=Ray3D(p.o,v)

        return ray.reflect(p.n,p.o)

    @staticmethod
    def planes_reflect(ps:[Point3D],ray:Vector3D)->[Ray3D]:
        rays=[]
        plane=Plane.from_three_points(ps[0],ps[1],ps[2])
        for p in ps:
            _v=p-ps[0]
            _plane=plane.move(_v)
            _ray=Glare_Analysis.plane_reflect(_plane,ray)
            rays.append(_ray)
        return rays

    @staticmethod
    def rays_project_mesh(rays:[Ray3D],amesh:Mesh3D)->Mesh3D|None:

        plane=Face3D(amesh.face_edges[0]).plane

        ps=[plane.intersect_line_ray(r) for r in rays]
        try:
            polyline=Polyline3D(ps)
            _m = Mesh3D(polyline.vertices, [(0, 1, 2, 3)])
            return _m
        except:
            return None

    @staticmethod
    def to3dmfile(meshs: [Mesh3D],resultindex,resultindex2,includegeo=True):
        _to = {}
        if includegeo!=True:
            dmbtye = write3dm(_to, {"meshindex": resultindex, "glassindex": resultindex2})
            return dmbtye
        rmesh = lmeshs_to_rmeshs(meshs)

        for index, m in enumerate(rmesh):
            if m != None:
                _to[index] = m
            else:
                continue
        dmbtye = write3dm(_to, {"meshindex": resultindex,"glassindex": resultindex2})
        return dmbtye

    def analysis_to_glass(self,result:list[CalResult],analysismeshindex:list[int])->list[int]:
        _r=[0 for i in self.building.faces]
        for index,r in enumerate(result):
            for a_index in analysismeshindex:
                if a_index in r.analysismeshindex2:
                    _r[r.glassindex]+=1
        return _r

    def glass_to_analysis(self,result:list[CalResult])->list[int]:
        result_index = [0 for i in self.analyaisgird.face_centroids]

        for i in result:
            for index in i.analysismeshindex:

                result_index[index] += 1
        return result_index

    def group_result(self,result):
        grouped_data ={}
        for item in result:
            sunindex = item.sunindex
            if sunindex not in grouped_data:
                grouped_data[sunindex] = []
            grouped_data[sunindex].append(item)
        return grouped_data

    def analysis_to_glass2(self,result:list[SunTranceResult],analysismeshindex:list[int])->list[int]:
        _r=[0 for i in self.building.face_centroids]
        #grouped_data = self.group_result(result)
        #print("toglass")

        for r in result:
            if r.m==None:
                continue
            else:
                if r.analysismeshindex in analysismeshindex:
                    _r[r.glassindex]+=1
        return _r



    def glass_to_analysis2(self,result:list[SunTranceResult])->list[int]:
        result_index = [0 for i in self.analyaisgird.face_centroids]
        grouped_data=self.group_result(result)

        for sunindex,results in grouped_data.items():
            anaindex=[]
            for r in results:
                if r.m==None:
                    continue

                if r.analysismeshindex in anaindex:
                    continue
                else:
                    anaindex.append(r.analysismeshindex)
                    result_index[r.analysismeshindex] += 1
        return result_index



