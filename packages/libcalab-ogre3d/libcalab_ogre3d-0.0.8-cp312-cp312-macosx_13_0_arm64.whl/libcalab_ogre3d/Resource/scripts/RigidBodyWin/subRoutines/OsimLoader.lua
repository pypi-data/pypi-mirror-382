
require("subRoutines/VRMLexporter")
-- convertToConvexes: moved to module.lua

local function parseV3(t)
	if type(t)~='string' then return t:copy() end
	local t=string.tokenize(t,'%s+')
	if #t>=4 then
		if (t[1]=='') then
			return vector3(tonumber(t[2]), tonumber(t[3]), tonumber(t[4]))
		elseif t[4]=='' then
			return vector3(tonumber(t[1]), tonumber(t[2]), tonumber(t[3]))
		else
			return nil
		end
	end

	assert(#t==3)
	return vector3(tonumber(t[1]), tonumber(t[2]), tonumber(t[3]))
end
local function parseV2(t)
	local t=string.tokenize(t,'%s+')
	assert(#t==2)
	return vector3(tonumber(t[1]), tonumber(t[2]), 0)
end
local function parseNum(t)
	local n={}
	local t=string.tokenize(t,'%s+')
	local n={}
	for i, v in ipairs(t) do
		if v~='' then
			table.insert(n, tonumber(v))
		end
	end
	return n
end

local function parsePoly(t)
	local n=parseNum(t)
	--  5 4 3 2 1
	--      6
	--
	local out={}
	local last=n[#n]
	for i=1, #n-2 do
		table.insert(out, vector3(n[i], n[i+1], last))
	end
	return out
end
local function parseV6(t)
	local t=string.tokenize(t,'%s+')
	assert(#t==6)
	return vector3(tonumber(t[1]), tonumber(t[2]), tonumber(t[3])), vector3(tonumber(t[4]), tonumber(t[5]), tonumber(t[6]))
end
local function parseVec(t)
	local t=string.tokenize(t,'%s+')
	for i, v in ipairs(t) do
		t[i]=tonumber(v)
	end
	return t
end
local function findAxis(st, coord)
	assert(st.TransformAxis[1].coordinates==coord._attr.name)
	return parseV3(st.TransformAxis[1].axis)
end
local OsimParser=LUAclass()
function OsimParser:__init(filename, options)
	self.options=options or {}

	local xml2lua = require("xml2lua/xml2lua")
	--Uses a handler that converts the XML to a Lua table
	local Handler= require("xml2lua/xmlhandler.tree")
	if type(filename)=='string' then
		if filename:sub(-9)=='.osim.lua'then
			local model_table=util.loadTableFromLua(filename)
			model_table.filename=filename
			for k,v in pairs(model_table) do
				self[k]=v
			end
			if options then
				-- overwrite
				for k, v in pairs(options) do
					self.options[k]=v
				end
			end

		else
			local handler=Handler:new()
			local xml = util.readFile(filename)

			--Instantiates the XML parser
			local parser = xml2lua.parser(handler)
			parser:parse(xml)

			self.bones={}
			self.boneNameToIdx={}

			local function jointType(Joint)
				if Joint.CustomJoint then
					return 1, Joint.CustomJoint 
				end
				if Joint.PinJoint then
					return 2, Joint.PinJoint 
				end
				if Joint.UniversalJoint then
					return 3, Joint.UniversalJoint 
				end
				if Joint.WeldJoint then
					return 4, Joint.WeldJoint 
				end
				return 0 
			end

			local model=handler.root.OpenSimDocument.Model
			local function rectifyMuscle(mscl)
				if mscl._attr and mscl._attr.name then
					mscl.name=mscl._attr.name
					mscl._attr=nil
				end
				do
					local o=mscl.GeometryPath.PathPointSet.objects
					mscl.GeometryPath.PathPointSet=o.PathPoint
					if #mscl.GeometryPath.PathPointSet==0 then
						mscl.GeometryPath.PathPointSet={o.PathPoint}
					end
					if o.ConditionalPathPoint then
						if #o.ConditionalPathPoint ==0 then
							o.ConditionalPathPoint={ o.ConditionalPathPoint}
						end
						for icpp, cpp in ipairs(o.ConditionalPathPoint) do
							local n=tonumber(cpp._attr.name:sub(-1))
							assert(n)
							cpp.type='ConditionalPathPoint'
							local tokens=string.tokenize(cpp.socket_coordinate,'%/')
							cpp.coordinate=tokens[#tokens]
							if cpp.range then
								cpp.range=string.tokenize(cpp.range,'%s')
								for i,v in ipairs(cpp.range) do
									cpp.range[i]=tonumber(cpp.range[i])
								end
							end
							assert(n>1)
							assert(tonumber(mscl.GeometryPath.PathPointSet[n-1]._attr.name:sub(-1))==n-1)
							table.insert(mscl.GeometryPath.PathPointSet, n, cpp)
						end
					end
					if o.MovingPathPoint then
						local n=tonumber(o.MovingPathPoint._attr.name:sub(-1))
						assert(n)
						assert(n>1)
						assert(tonumber(mscl.GeometryPath.PathPointSet[n-1]._attr.name:sub(-1))==n-1)
						o.MovingPathPoint.isMoving=true
						assert(tonumber(mscl.GeometryPath.PathPointSet[n-1]._attr.name:sub(-1))==n-1)
						table.insert(mscl.GeometryPath.PathPointSet, n, o.MovingPathPoint)
					end
				end
				if mscl.GeometryPath.PathPointSet then
					for i, v in ipairs(mscl.GeometryPath.PathPointSet) do
						v.name=v._attr.name
						v._attr=nil
						v.joint=v.body

						if v.location then
							v.location=parseV3(v.location)
						else
							print('warning: ignoring SimmSpline of pathPoint '..v.name ..' ('..mscl.name..')')
							v.location=vector3()
							--v.location.x=tonumber(v.x_location.SimmSpline.y:tokenize('%s+')[1])
							--v.location.y=tonumber(v.y_location.SimmSpline.y:tokenize('%s+')[1])
							--v.location.z=tonumber(v.z_location.SimmSpline.y:tokenize('%s+')[1])
							local x_index=table.find(v.x_location.SimmSpline.x:tokenize('%s+'),"0")
							local y_index=table.find(v.y_location.SimmSpline.x:tokenize('%s+'),"0")
							local z_index=table.find(v.z_location.SimmSpline.x:tokenize('%s+'),"0")
							if z_index==nil then z_index=1; end
							v.location.x=tonumber(v.x_location.SimmSpline.y:tokenize('%s+')[x_index])
							v.location.y=tonumber(v.y_location.SimmSpline.y:tokenize('%s+')[y_index])
							v.location.z=tonumber(v.z_location.SimmSpline.y:tokenize('%s+')[z_index])
						end

						if v.body ==nil then
							assert(v.socket_parent_frame)
							assert(v.socket_parent_frame:sub(1,9)=='/bodyset/')
							v.joint=v.socket_parent_frame:sub(10)
						end
					end
				end
			end

			if model.defaults then
				self.defaultMuscle=model.defaults.Millard2012EquilibriumMuscle 
				rectifyMuscle(self.defaultMuscle)
			end

			self.coordinateActuator=model.ForceSet.objects.CoordinateActuator
			self.muscles=model.ForceSet.objects.Millard2012EquilibriumMuscle or model.ForceSet.objects.Thelen2003Muscle
			for i,v in ipairs(self.muscles) do
				rectifyMuscle(v)
			end

			self.coordActuatorNames={}
			if self.coordinateActuator then
				for i, v in ipairs(self.coordinateActuator) do
					self.coordActuatorNames[v.coordinate]=true
				end
			end

			--{{{ etri-specific begin
			do
				if model.BodySet.objects.Body[1].mass~='0' then
					table.insert(model.BodySet.objects.Body,1,
					{
						Joint={},
						VisibleObject={show_axes="false", transform="-0 0 -0 0 0 0", scale_factors="1 1 1", },
						_attr={name="ground", },
						inertia_xx='0', inertia_xy='0', inertia_xz='0', inertia_yy='0', inertia_yz='0', inertia_zz='0', mass='0', mass_center='0 0 0',
					})
				end
				local name_to_boneIndex={}
				for i, body in ipairs(model.BodySet.objects.Body) do
					name_to_boneIndex['/bodyset/'..body._attr.name]=i-1
				end

				local jointSet={}
				if model.JointSet then
					local function packJoint(jointSet, joint, jtype)
						table.insert(jointSet, joint)
						if joint.coordinates then
							joint.coordinates=joint.coordinates.Coordinate
						end

						assert(#joint.frames.PhysicalOffsetFrame==2)

						local frame1=joint.frames.PhysicalOffsetFrame[1]
						local frame2=joint.frames.PhysicalOffsetFrame[2]

						if frame1._attr.name==joint.socket_child_frame then
							assert(false)
						else
							assert(frame2._attr.name==joint.socket_child_frame)
						end

						local bid1=name_to_boneIndex[frame1.socket_parent] 
						local bid2=name_to_boneIndex[frame2.socket_parent] 
						if not bid1 then
							assert(frame1.socket_parent=='/ground')
						end
						assert(bid2)

						do
							local body=model.BodySet.objects.Body[bid2+1]
							assert(body.Joint==nil)
							assert(body.frame==nil)
							if jtype==1 then
								body.Joint={
									CustomJoint=joint
								}
							elseif jtype==2 then
								body.Joint={
									PinJoint=joint
								}
							elseif jtype==3 then
								body.Joint={
									UniversalJoint=joint
								}
							elseif jtype==4 then
								body.Joint={
									WeldJoint=joint
								}
							end
							joint.parent_body=string.sub(frame1.socket_parent, string.len('/bodyset/')+1)
							--assert(frame1.orientation=='0 0 0')
							--assert(frame2.orientation=='0 0 0')
							joint.location_in_parent=parseV3(frame1.translation)-parseV3(frame2.translation)
							if joint.SpatialTransform and joint.SpatialTransform.TransformAxis[1].SimmSpline then

								print('warning: ignoring SimmSpline of joint '..joint._attr.name )
								local ta=joint.SpatialTransform.TransformAxis
								assert(ta[4]._attr.name=='translation1')
								assert(ta[4].axis:sub(1,1)=='1') -- x axis
								assert(ta[5].axis:sub(1,3)=='0 1') -- y axis
								local offset=vector3()
								offset.x=tonumber(ta[4].SimmSpline.y:tokenize('%s+')[1])
								offset.y=tonumber(ta[5].SimmSpline.y:tokenize('%s+')[1])
								if ta[6].SimmSpline then
									offset.z=tonumber(ta[6].SimmSpline.y:tokenize('%s+')[1])
								else
									offset.z=tonumber(ta[6].Constant.value)
								end
								joint.location_in_parent:radd(offset)

							end
							joint.orientation_in_parent=frame1.orientation
							--assert(frame2.translation=='0 0 0') -- head offset seems to be buggy
							print(body._attr.name,', parent='.. joint.parent_body..', joint='.. joint._attr.name, joint.location_in_parent)
						end
					end
					for i, joint in ipairs(model.JointSet.objects.CustomJoint) do
						packJoint(jointSet, joint, 1)
					end
					for i, joint in ipairs(model.JointSet.objects.PinJoint) do
						packJoint(jointSet, joint, 2)
					end
					for i, joint in ipairs(model.JointSet.objects.UniversalJoint) do
						packJoint(jointSet, joint, 3)
					end
					for i, joint in ipairs(model.JointSet.objects.WeldJoint) do
						packJoint(jointSet, joint, 4)
					end
				end
			end
			--{{{ etri-specific end


			for i, body in ipairs(model.BodySet.objects.Body) do

				local jtype, joint=jointType(body.Joint)
				if jtype~=0 then
					local bone={}
					self.bones[i-1]=bone
					bone.name=body._attr.name
					self.boneNameToIdx[bone.name]=i-1
					bone.mass=tonumber(body.mass)
					bone.localCOM=parseV3(body.mass_center)

					--if bone.name:find("patella_r") then dbg.console() end
					--print(i, body._attr.name, ':::')

					if not body.inertia_xx then
						assert(body.inertia)
						local i1,i2=parseV6(body.inertia)
						bone.inertia=i1
						assert(i2.x==0)
					else
						bone.inertia=vector3(
						tonumber(body.inertia_xx),
						tonumber(body.inertia_yy),
						tonumber(body.inertia_zz))
						assert(body.inertia_xy=='0')
					end
					local vo=body.VisibleObject
					if vo then
						local geom=vo.GeometrySet.objects
						assert(geom)
						local dg=geom.DisplayGeometry 
						if dg then
							bone.geomFiles={}
							for i, v in ipairs(dg) do
								bone.geomFiles[i]=v.geometry_file
							end
							if dg.geometry_file then
								table.insert(bone.geomFiles, dg.geometry_file)
							end
						end
					elseif body.attached_geometry then
						bone.geomFiles={}
						local mesh=body.attached_geometry.Mesh
						if #mesh==0 then
							mesh={mesh}
						end
						for i, mesh in ipairs(mesh) do
							--assert(mesh.scale_factors=='1 1 1')
							assert(mesh.mesh_file)
							--print(bone.name, mesh.mesh_file)
							table.insert(bone.geomFiles, mesh.mesh_file)
						end
					end
					bone.pid=self.boneNameToIdx[joint.parent_body]
					bone.offset=parseV3(joint.location_in_parent)
					--if bone.name:find("patella_r") then bone.offset=bone.offset+vector3(0.0524,-0.0108,0.0027499999999999998) end
					--if bone.name:find("patella_l") then bone.offset=bone.offset+vector3(0.0524,-0.0108,-0.0027499999999999998) end
					-- joint orientation: Current orientation of the joint expressed in the local body frame in body-fixed X-Y-Z Euler angles.
					bone.jointOrientation=quater()
					bone.jointOrientation:setRotation("xyz", parseV3(joint.orientation_in_parent))


					local coord=joint.coordinates
					if not coord and joint.CoordinateSet then
						coord=joint.CoordinateSet.objects.Coordinate
					end

					if jtype==2 or (jtype==1 and #coord==0) then
						-- pin joint
						bone.jointType='rotate'
						bone.jointAxis=bone.jointOrientation*vector3(0,0,1)

						if jtype==1 then
							bone.jointAxis=bone.jointOrientation*findAxis(joint.SpatialTransform, coord)
						end
						local range=parseV2( coord.range)
						if range.x>-1.57 or range.y<1.57 then
							bone.range=range
						end
					elseif jtype==3 then
						-- universal joint
						bone.jointType='rotate'
						bone.jointAxis={
							bone.jointOrientation*vector3(1,0,0),
							bone.jointOrientation*vector3(0,1,0),
						}
					elseif jtype==4 then
						-- fixed joint
						bone.jointType='fixed'
					elseif false then
						for i=1,3 do
							local range=parseV2( coord[i].range)
							assert(range.x<-1.57)
							assert(range.y>1.57)
						end
					end
					if coord==nil then
						coord={}
					elseif #coord==0 then
						coord={coord}
					end

					local locked=true
					local actuated=false
					--if bone.name=='tibia_r' then dbg.console() end
					for i, v in ipairs(coord) do
						if v.locked=='false' then
							locked=false
						end
						if self.coordActuatorNames[v._attr.name] then
							actuated=true
						end
					end
					if locked then
						bone.jointType='fixed'
						bone.locked=true
					end
					bone.actuated=actuated
					if vo then
						bone.transform={parseV6(vo.transform)}
						bone.scale_factors=parseV3(vo.scale_factors)
					end
				else
					--dbg.console()
				end
			end
			self.model_name=model._attr.name or 'robot'
			self.filename=filename
		end
	else
		assert(type(filename)=='table')
		for k,v in pairs(filename) do
			self[k]=v
		end
		if options then
			-- overwrite
			for k, v in pairs(options) do
				self.options[k]=v
			end
		end
	end
	local out=VRMLexporter.generateWRLstring(self.bones, self.model_name , self.filename)
	local file=CTextFile()
	file:OpenMemory(out)
	local loader=MainLib.VRMLloader(file)
	self.loader=loader
	loader:print()


	local bones=self.bones
	local path=os.parentPath(self.filename)

	self.actuated=boolN(loader:numBone())
	self.actuated:setAllValue(false)
	local Actuated_bones=self.options.actuated_bones or {
		--for Rajagopal Original (Fulllbody-4.0 version 30000)
		"torso",
		"humerus_r",
		"ulna_r",
		"radius_r",
		"hand_r",
		"humerus_l",
		"ulna_l",
		"radius_l",
		"hand_l",
	}
	if self.options.RAJAGOPAL_LIBS then
		Actuated_bones={
		"humerus_r",
		"ulna_r",
		"radius_r",
		"hand_r",

		"humerus_l",
		"ulna_l",
		"radius_l",
		"hand_l",
	}

	end
	for ibone=1, loader:numBone()-1 do
		local bone=loader:VRMLbone(ibone)
		if not bone:hasShape() then
			bone:createNewShape()
		end
		local boneInfo=bones[self.boneNameToIdx[bone:name()]]
		if boneInfo.actuated then
			self.actuated:set(ibone, true)
		end
		for j=1,table.count(Actuated_bones) do
			if bone:name()==Actuated_bones[j] then
				self.actuated:set(ibone, true)
			end
		end
		if bones[ibone].geomFiles then
			local mesh=bone:getMesh()

			local newmesh=Mesh()

			if self.options.debugDraw then
				dbg.draw('Axes', bone:getFrame()*transf(boneInfo.jointOrientation), 'joint'..ibone, 100)
			end
			for j, geomFile in ipairs(boneInfo.geomFiles) do
				local xml = util.readFile(path..'/Geometry/'..geomFile)
				if xml then
					local handler=Handler:new()
					--Instantiates the XML parser
					local parser = xml2lua.parser(handler)
					parser:parse(xml)

					local no=handler.root.VTKFile.PolyData.Piece.PointData.DataArray
					local da=handler.root.VTKFile.PolyData.Piece.Polys.DataArray
					local po=handler.root.VTKFile.PolyData.Piece.Points.DataArray

					no=string.lines(no[1])
					po=string.lines(po[1])
					local index=string.lines(da[1][1])

					local function dataToVector3N(po)
						local vertices=vector3N(#po)
						vertices:setSize(0)

						for i, n in ipairs(po) do
							local nn=parseNum(n)
							if #nn>=3 then
								vertices:pushBack(vector3(nn[1], nn[2], nn[3]))
							end
							if #nn>=6 then
								vertices:pushBack(vector3(nn[4], nn[5], nn[6]))
								assert(#nn==6)
							end
						end
						return vertices
					end
					local vertices=dataToVector3N(po)
					local normals=dataToVector3N(no)
					local indices=intvectorn()
					indices:setSize(#index*3) -- reserve
					indices:resize(0)

					for i, n in ipairs(index) do
						local ii=parsePoly(n)
						for j, vec in ipairs(ii) do
							indices:pushBack(vec.x)
							indices:pushBack(vec.y)
							indices:pushBack(vec.z)
							assert(vec.x<vertices:size())
							assert(vec.y<vertices:size())
							assert(vec.z<vertices:size())
							assert(vec.x>=0)
							assert(vec.y>=0)
							assert(vec.z>=0)
						end
					end
					assert(indices:size()>3)

					if boneInfo.geomTransform then
						for i=0, vertices:size()-1 do
							vertices(i):assign(boneInfo.geomTransform *vertices(i))
						end
					end

					local tmesh=Mesh()
					tmesh:init(vertices, normals, indices)
					newmesh:mergeMesh(newmesh, tmesh)
				else
					assert(false)
				end
			end
			if newmesh:numVertex()>0 then
				print('shapeAdded:', bone:name())
				mesh:assignMesh(newmesh)
			else
				dbg.console()
				mesh:initBox(vector3(0.1,0.1,0.1))
				--assert(false)
			end
		end
		if boneInfo.range and not boneInfo.locked then
			bone:setJointRange(0, math.deg(boneInfo.range.x),math.deg(boneInfo.range.y))
		end
		bone:setMass(boneInfo.mass)
		bone:setInertia(boneInfo.inertia.x, boneInfo.inertia.y, boneInfo.inertia.z)
	end
	--loader:convertToConvexes()

	self:_initPathPoints()
end

function OsimParser:toTable()
	local bones=deepCopyTable(self.bones)
	for i, v in ipairs(bones) do 
		v.children=nil
	end
	local muscles=deepCopyTable(self.muscles)
	for i, muscle in ipairs(muscles) do
		muscle.GeometryPath._attr=nil
		assert( muscle.GeometryPath.PathPointSet)
		for k, pp in ipairs(muscle.GeometryPath.PathPointSet) do
			pp.location=nil
		end
	end

	return {
		bones=bones,
		boneNameToIdx=self.boneNameToIdx,
		coordinateActuator=self.coordinateActuator,
		muscles=muscles,
		options=self.options,
		model_name=self.model_name,
		filename=self.filename..'.lua'
	}
end

function OsimParser:removeFixedJoints()
	local mLoaderFixedJoints={}
	local mLoader=self.loader
	for i=1, mLoader:numBone()-1 do
		local bone=mLoader:VRMLbone(i)
		if bone:HRPjointType(0)==MainLib.VRMLTransform.FIXED then
			print(bone:name())
			mLoaderFixedJoints[bone:name()]={ bone:parent():name(), bone:getOffset() }
		end
	end
	mLoader:removeAllRedundantBones()
	self.fixedJoints=mLoaderFixedJoints
end

function OsimParser:_initPathPoints()
	local muscles=self.muscles
	-- pathpoints
	self.pathpoints = {}
	for i_muscle, muscle in ipairs(muscles) do
		self.pathpoints[i_muscle]={}
		for j, pp in ipairs(muscle.GeometryPath.PathPointSet) do
			pp.muscleindex = i_muscle
			pp.treeIndex=self.loader:getTreeIndexByName(pp.joint)
			if(pp.treeIndex<1) then
				local fixedJointInfo=self.fixedJoints[pp.joint]
				pp.treeIndex=self.loader:getTreeIndexByName(fixedJointInfo[1])
				assert(pp.treeIndex>=1)
				pp.location=pp.location+fixedJointInfo[2]
			end
			table.insert(self.pathpoints[i_muscle], pp)
		end
	end
end

function OsimParser:getMuscleList(options)
	local muscles={}
	if not self.pathpoints then
		self:_initPathPoints()
	end
	for i_muscle, muscle in ipairs(self.muscles) do
		local muscleInfo={}

		table.insert(muscleInfo, i_muscle)
		table.insert(muscleInfo, muscle.name)
		table.insert(muscleInfo, #self.pathpoints[i_muscle])

		for j, pp in ipairs(self.pathpoints[i_muscle]) do
			table.insert(muscleInfo, pp.treeIndex)
			if not pp.location then
				pp.location=vector3(unpack(pp.location_wrl))
			end
			if options and options.YtoZ then
				table.insert(muscleInfo, pp.location:YtoZ())
			else
				table.insert(muscleInfo, pp.location)
			end
		end
		table.insert(muscles, muscleInfo)
	end

	return muscles
end

function OsimParser:getPathPointPositionsGlobal(i_muscle)

	local out=vector3N()
	local bfk=self.loader:fkSolver()
	for i_pp, pathPoint in ipairs(self.pathpoints[i_muscle]) do
		local j = self.loader:bone(pathPoint.treeIndex)
		local lp = pathPoint.location
		if not pathPoint.location then
			pathPoint.location=vector3(unpack(pathPoint.location_wrl))
			lp=pathPoint.location
		end
		--local gp = j:getFrame():toGlobalPos(tbl2vec3(lp))
		local gp = bfk:globalFrame(j):toGlobalPos(lp)
		out:pushBack(gp)
	end
	return out
end
function OsimParser:drawMuscles()
	-- todo : conditional path points
	if not self.objectList then
		self.objectList=Ogre.ObjectList()
	end
	local objectList=self.objectList
	local lineWidth=1
	local lines =vector3N()
	local skinScale=100
	for i_muscle, path_points in ipairs(self.pathpoints) do
		local ppPosz = self:getPathPointPositionsGlobal(i_muscle)
		for j=0,ppPosz:size()-2 do
			lines:pushBack((ppPosz(j))*skinScale)
			lines:pushBack((ppPosz(j+1))*skinScale)
			lines:pushBack((vector3(1, 0,0))) -- color
		end
	end

	if lines:rows()>0 then
		dbg.drawBillboard(lines:matView(), 'muscles', 'use_vertex_color', lineWidth, 'ColorBillboardLineList')
	end
end
return OsimParser
