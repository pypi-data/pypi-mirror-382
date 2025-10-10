
require("config")
package.projectPath='../Samples/classification/'
package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path

require("module")
require("common")
require("subRoutines/RayBoxCheck")

SceneComponent=LUAclass()
SceneComponent.PLANE=1
SceneComponent.TERRAIN=2
SceneComponent.ENTITY=3
SceneComponent.NONE=4



function createNodeandEntity(rootnode,pInfo)
	local pNode=RE.createChildSceneNode(rootnode,pInfo.nodeId)
	local Entitynode={}
	local Entitynode=RE.ogreSceneManager()
	local entity=Entitynode:createEntity("_entity_"..pInfo.nodeId,pInfo.source)
	return pNode,entity
end

function SceneComponent:__init(t)
	self.scType=t
	self.pos=vector3(0,50,0)
	self.scale=vector3(1,1,1)
	self.ori=quater(1,0,0,0)
	self.bCastShadow=true
	self.bNormaliseNormals=true
	self.options=intvectorn()

	if (self.scType==SceneComponent.PLANE) then
		self.nodeId="plane000"
		self.material="Crowd/Board"
		self.options:setValues(4000,4000,20,20)
	elseif (self.scType==SceneComponent.ENTITY) then
		self.nodeId='entity000'
		self.material=""
		self.source='h11.mesh'
	elseif (self.scType==SceneComponent.TERRAIN) then
		self.nodeId="terrain000"
		self.material="Crowd/Terrain"
		self.source="../Resource/crowdEditingScripts/terrain/heightmap1_256_256_2bytes.raw"
		self.options:setValues(256, 256, 1000,1000,50,1,1)
		self.bCastShadow=false
	end
end

-- call manually!
function SceneComponent:__finalize()
	local child=RE.ogreSceneManager():getSceneNode(self.nodeId)
	RE.removeEntity(child)
end

function SceneComponent:getScript()
	local out={}
	table.insert(out,"pos:set("..self.pos.x..","..self.pos.y..","..self.pos.z..")")
	table.insert(out,"scale:set("..self.scale.x..","..self.scale.y..","..self.scale.z..")")
	table.insert(out,"ori:setValue("..self.ori.w..","..self.ori.x..","..self.ori.y..","..self.ori.z..")")
	if self.scType==SceneComponent.ENTITY then
		table.insert(out,"material=''")
	else
		table.insert(out,"material='"..self.material.."'")
	end
	if self.scType==SceneComponent.ENTITY  then
		table.insert(out,"source= '"..self.source.."'")
	else 
		table.insert(out,"source=''")
	end

	if(self.bCastShadow) then
		table.insert(out,"bCastShadow=true")
	else
		table.insert(out,"bCastShadow=false")
	end
	if(self.options:size()==4) then
		table.insert(out,"options:setValues("..self.options(0)..","..self.options(1)..","..self.options(2)..","..self.options(3)..")")
	elseif(self.options:size()==6) then
		table.insert(out,"options:setValues("..self.options(0)..","..self.options(1)..","..self.options(2)..","..self.options(3)..","..self.options(4)..","..self.options(5)..")")
	elseif(self.options:size()==7) then
		table.insert(out,"options:setValues("..self.options(0)..","..self.options(1)..","..self.options(2)..","..self.options(3)..","..self.options(4)..","..self.options(5)..","..self.options(6)..")")
	end
	return table.concat(out, '\n')
end


function dbgDraw(name, pos, color)
	color = color or 'blue'
	dbg._namedDraw('Sphere', pos, name, color, 5)
end

function getTransform(pNode)
	local tt=matrix4()
	tt:setTransform(pNode:getPosition(), pNode:getScale(), pNode:getOrientation())
	return tt
end
function setTransform(pNode,pInfo)
	pNode:setPosition(pInfo.pos)
	pNode:setScale(pInfo.scale)
	pNode:setOrientation(pInfo.ori)
end



function SceneComponent:redraw()
	local entity
	local pNode

	local rootnode=RE.ogreRootSceneNode()
	if(self.scType==SceneComponent.PLANE) then
		if((self.options:size())~=4 and (self.options:size())~=6) then
			Msg:MsgBox("error! plane should have 4 or 6 parameters:(width,height,nx,ny,ntx=1,nty=1)")
			return
		end
		pNode=RE.createChildSceneNode(rootnode,self.nodeId)
		if(self.options:size()==4) then
			entity=RE.createPlane("_entity_"..self.nodeId,self.options(0),self.options(1),self.options(2),self.options(3),1,1)
		else
			entity=RE.createPlane("_entity_"..self.nodeId,self.options(0),self.options(1),self.options(2),self.options(3),self.options(4),self.options(5))
		end
	elseif(self.scType==SceneComponent.TERRAIN) then
		pNode=RE.createChildSceneNode(rootnode,self.nodeId)
		entity=RE.createTerrain("_entity_"..self.nodeId,self.source,self.options(0),self.options(1),self.options(2),self.options(3),self.options(4),self.options(5),self.options(6))
	else
		pNode,entity=createNodeandEntity(rootnode,self)
	end
	setTransform(pNode,self)

	if string.len(self.material)>0 then
		entity:setMaterialName(self.material)
	end
	if not (self.bCastShadow) then
		entity:setCastShadows(self.bCastShadow)
	end
	pNode:attachObject(entity)	
end


browserGraph={}

function copyInfo(v)
	return {
		scType=v.scType,
		nodeId=v.nodeId,
		options=v.options:copy(),
		pos=v.pos:copy(),
		ori=v.ori:copy(),
		scale=v.scale:copy(),
		material=v.material,
		bCastShadow=v.bCastShadow,
		bNormaliseNormals=v.bNormaliseNormals,
		source=v.source,
	}
end
function browserGraphToTable()
	local out={}
	local browser=this:findWidget('clip board')
	for i=1,browser:browserSize() do
		local id=browser:browserText(i)
		local v=browserGraph[id]
		-- copy only important informations
		out[i]=copyInfo(v)
	end
	return out
end
function findSceneComponent(node_name)
	if browserGraph[node_name] then
		return true
	end
	return false
end

function findCollidingSceneComponent(pgraph)
	for k, v in pairs(browserGraph) do
		if k.nodeId~=k then
			if pgraph.pos:distance(v.pos)<60 then
				return true
			end
		end
	end
	return false
end
function addToBrowser(pgraph)
	while(findSceneComponent(pgraph.nodeId)) do
		pgraph.nodeId=string.sub(pgraph.nodeId, 1,-4)..string.format('%03d', tonumber(string.sub(pgraph.nodeId, -3))+1)
	end
	while(findCollidingSceneComponent(pgraph)) do
		if math.random()<0.5 then
			pgraph.pos.x=pgraph.pos.x+100
		else
			pgraph.pos.z=pgraph.pos.z+100
		end
	end
	browserGraph[pgraph.nodeId]=pgraph
	pgraph:redraw()
	local browser=this:findWidget('clip board')
	browser:browserAdd(pgraph.nodeId)
	browser:redraw()
end

function ctor()
	RE.ogreSceneManager():setFogNone() -- turn off fog (so that the following skybox is visible)

	--dbg.startTrace2() -- to see where the program crashes, 1. uncomment this line, 2. run, and 3. see work/trace.txt
	mObjectList=Ogre.ObjectList()

	this:create("Choice", "global operations","global operations")
	this:widget(0):menuSize(6)
	this:widget(0):menuItem(0,"global operations")
	this:widget(0):menuItem(1,"create plane",'p')
	this:widget(0):menuItem(2,"create terrain",'o')
	this:widget(0):menuItem(3,"create h11",'h')
	this:widget(0):menuItem(4,"save scene",'FL_CTRL+s')
	this:widget(0):menuItem(5,"load scene",'FL_CTRL+o')

	this:widget(0):menuValue(0)



	this:setWidgetHeight(100)
	this:create("Multi_Browser","clip board","clip board",0)



	this:resetToDefault()
	this:newLine()
	this:setWidgetHeight(100)

	this:create("Multiline_Input","script",0)

	this:resetToDefault()

	this:create("Button","Run script","change property")
	this:newLine()

	this:create("Check_Button","snap to grid","snap to grid")
	this:widget(0):checkButtonValue(1)

	this:create("Choice", "edit mode","edit mode",1)
	this:widget(0):menuSize(10)
	this:widget(0):menuItem(0,"none",'n')
	this:widget(0):menuItem(1,"translate",'t')
	this:widget(0):menuItem(2,"rotate",'r')
	this:widget(0):menuItem(3,"scale",'s')
	this:widget(0):menuItem(4,"translate Y",'f')
	this:widget(0):menuItem(5,"CLICK: remove",'q')
	this:widget(0):menuItem(6,"CLICK: duplicate",'y')
	this:widget(0):menuItem(7,"CLICK: rotate 90 about X",'z')
	this:widget(0):menuItem(8,"CLICK: rotate 90 about Y",'x')
	this:widget(0):menuItem(9,"CLICK: rotate 90 about Z",'c')

	this:widget(0):menuValue(1)

	this:create("Choice","change material","change material")

	this("menuAddItem", "change material", {
		{"Crowd materials", "Crowd/Blue","cagotruck.material", "Crowd/Red", "Crowd/Green", "Crowd/Red", "Crowd/Dirt", 
		"Crowd/Dirt01", "Crowd/EgyptRocky", "Crowd/MtlPlat2", "Crowd/RustedMetal", "Crowd/TerrRock", "Crowd/Terrain", 
		"CrowdEdit/Terrain1"},
		{"Solid colors", "solidblue", "solidblack", "solidred", "solidlightgreen", "solidgreen", "solidwhite"},
		{"Colors", "green", "white", "black","blue","red","lightgrey"},
		{"Icons", "blueCircle", "redCircle", "icons/add", "icons/refresh","LAKEREM"}
	})

	this:create("Choice","change source", "change source")

	this("menuAddItem", "change source", {
		{"Simple polygons", "sphere1010.mesh", "arrow.mesh", "cone.mesh", "axes.mesh", "cylinder.mesh"},
		{"Static objects", "pave.mesh","cagotruck.mesh", "ogrehead.mesh"},
		{"Ogre default meshes", "ogrehead.mesh", "athene.mesh", "Barrel.mesh", "column.mesh", "cube.mesh", "facial.mesh", "fish.mesh", "geosphere4500.mesh",
		"geosphere8000.mesh", "knot.mesh", "ninja.mesh", "razor.mesh", "RZR-002.mesh", "sphere.mesh", "WoodPallet.mesh"},
		{"Dynamic objects",  "muaythai1.mesh"},
	})

	this:create("Choice","house","house")
	this:widget(0):menuSize(6)
	this:widget(0):menuItem(0,"type 1",'6')
	this:widget(0):menuItem(1,"type 2",'7')
	this:widget(0):menuItem(2,"type 3",'8')
	this:widget(0):menuItem(3,"type 4",'9')
	this:widget(0):menuItem(4,"type 5",'0')
	this:widget(0):menuItem(5,"type 6",'-')

	this:create("Choice","create item")
	this:widget(0):menuSize(8)
	this:widget(0):menuItem(0,"choose item")
	this:widget(0):menuItem(1,"item 1",'6')
	this:widget(0):menuItem(2,"item 2",'7')
	this:widget(0):menuItem(3,"item 3",'8')
	this:widget(0):menuItem(4,"item 4",'9')
	this:widget(0):menuItem(5,"item 5",'0')
	this:widget(0):menuItem(6,"item 6",'-')
	this:widget(0):menuItem(7,"item 7",'=')

	this:create("Button", "build all houses", "build all houses")


	this:updateLayout()

end

function dtor()
	local browser=this:findWidget('clip board')
	for i=1,browser:browserSize() do
		browserGraph[browser:browserText(i)]=nil
	end
	mObjectList:clear()

	collectgarbage()
end

function FindCollisionEntity(ray)
	for i,v in pairs (browserGraph) do
		childnode=RE.ogreSceneManager():getSceneNode(v.nodeId)
		childnode:showBoundingBox(false)
	end
	local min_o=1e9
	local argMin=nil
	for i,pInfo in pairs (browserGraph) do
		local childnode=RE.ogreSceneManager():getSceneNode(pInfo.nodeId)
		local MatrixInfo=getTransform(childnode)
		local bbmin=vector3(0,0,0)
		local bbmax=vector3(0,0,0)
		local entity=RE.ogreSceneManager():getSceneNode(pInfo.nodeId):getEntity()
		entity:getBoundingBox(bbmin,bbmax)

		bret, o=rayIntersectsBox(ray, bbmin, bbmax, MatrixInfo)
		--childnode:setPosition(currentcursorPos.x,currentcursorPos.y,currentcursorPos.z)
		if bret and o<min_o then
			min_o=o
			argMin={pInfo, bret, o}
		end
	end
	if argMin then
		return unpack(argMin)
	end
	return nil, false, 0
end

function foreachSelected(fcn, bBreak)
	local browser=this:findWidget('clip board')
	for i=1,browser:browserSize() do

		if (browser:browserSelected(i)) then
			local graph=getInfo(browser, i)
			local child=RE.ogreSceneManager():getSceneNode(graph.nodeId)
			fcn(graph, child, browser, i)
			if bBreak then
				break
			end
			setTransform(child, graph)
		end
	end
end
function handleRendererEvent(ev,button,x,y)
	if ev =="PUSH" or 
		ev=="MOVE" or
		ev=="DRAG" or
		ev=="RELEASE" then
		--[[
		local w=math.rad(currentcursorPos.x)
		child:setOrientation(w,0,1,0)
		--]]
		print(ev)
		local pInfo
		local MatrixInfo
		local entity
		--local childnode
		local bret=false
		local o

		local ray = Ray()
		RE.FltkRenderer():screenToWorldRay(x,y,ray)

		local PLANE_HEIGHT=1.0;
		local tt=Plane (vector3(0,1,0), PLANE_HEIGHT);
		local r=ray:intersects(tt)
		local currentcursorPos=ray:getPoint(r(1))
		dbgDraw("cc",currentcursorPos,'blue')


		if (ev=='PUSH' or ev=='RELEASE' or ev=='DRAG') then

			local editMode=this:findWidget('edit mode'):menuText()

			if string.sub(editMode, 1,5)=='CLICK' then
				editMode=string.sub(editMode, 8)
				if ev=='RELEASE' then
					if editMode=='remove' then
						foreachSelected(
						function(graph, child,browser, i) 
							graph:__finalize()
							browserGraph[graph.nodeId]=nil
							browser:browserRemove(i)
						end, 
						true)
					elseif editMode=='duplicate' then
						foreachSelected(
						function(graph, child,browser, i) 
							local info=SceneComponent(graph.scType)
							local ci=copyInfo(graph)
							for k, v in pairs(ci) do
								info[k]=v
							end
							addToBrowser(info)
						end, 
						true)
					elseif string.sub(editMode, 1,9) =='rotate 90' then
						local q
						if string.sub(editMode, -1)=='X' then
							q=quater(math.rad(90), vector3(1,0,0))
						elseif string.sub(editMode, -1)=='Y' then
							q=quater(math.rad(90), vector3(0,1,0))
						else
							q=quater(math.rad(90), vector3(0,0,1))
						end
						foreachSelected(function(graph, child) graph.ori:leftMult(q) end)
					else
						print('not implmented yet '..editMode)
					end
				end
				return 1;
			end

			if ev=='PUSH' then
				g_pushed={
					x=x, 
					y=y, 
					cursorPos=currentcursorPos:copy()
				}
			end

			if editMode~='none' then
				return handleEditingEvent(g_pushed, {x=x, y=y, cursorPos=currentcursorPos:copy()}, ev, editMode )
			end
			return 1;

		elseif ev=='MOVE' then
			local menu=this:findWidget("edit mode")
			menu:activate()

			local pInfo,bret,o=FindCollisionEntity(ray)
			deselectAll()
			if bret then
				selectfunc(pInfo.nodeId)
			end
			return 1
		end
	end
	return 0
end

function selectfunc(id)
	local browser=this:findWidget('clip board')
	for i=1,browser:browserSize() do
		if (id==browser:browserText(i)) then
			if not (browser:browserSelected(i)) then
				browser:browserSelect(i)
			end
		end
	end

	local graph=browserGraph[id]
	local child=RE.ogreSceneManager():getSceneNode(graph.nodeId)
	child:showBoundingBox(true)
end

function deselect(id)
	local browser=this:findWidget('clip board')

	local pInfo={}
	pInfo=browserGraph[id]

	for i=1,browser:browserSize() do
		if id==browser:browserText(i) then
			if browser:browserSelected(i) then
				browser:browserSelect(i)
				break
			end
		end
	end
	local childnode=RE.ogreSceneManager():getSceneNode(pInfo.nodeId)
	childnode:showBoundingBox(false)
end

function getInfo(browser, i)
	local id
	id=browser:browserText(i)
	local pInfo=browserGraph[id]
	return pInfo
end

function updateScript()
	local browser=this:findWidget('clip board')
	local _input=this:findWidget('script')
	for i=1,browser:browserSize() do
		if browser:browserSelected(i) then
			local pInfo=getInfo(browser, i)
			_input:inputValue(pInfo:getScript())
			_input:redraw()
			return
		end
	end

	_input:inputValue("")
	this:redraw()
end

function buildHouse(i,j)
	local entity=SceneComponent(SceneComponent.ENTITY)
	if i==1 or i==6 then
		if j>5 then
			-- mesh does not exist.
			return 
		end
	end
	local id=string.format("%d%d",i,j)
	entity.source=string.format("h%s.mesh",id)
	entity.nodeId=string.format("h%s_000",id)
	entity.pos.y=50

	if((i==1 and j ==5) or (i==3 and j == 6) or (i==31 and j ==5) or (i==4 and j ==5) or (i==4 and j==2)) then
		entity.pos.x=50	
	end
	addToBrowser(entity)
	selectfunc(entity.nodeId)
end
function onCallback(w,pWidget, userData)

	if(w:id()=="create item") then
		if not (w:menuValue() ==0) then

			local i= this:findWidget("house"):menuValue()+1
			local j= w:menuValue()

			buildHouse(i,j)
		end
	elseif(w:id()=="build all houses") then
		for i=1,6 do
			for j=1,7 do
				buildHouse(i,j)
			end
		end
	elseif(w:id()=="change material") then
		local browser=this:findWidget('clip board')
		for i=1,browser:browserSize() do
			if browser:browserSelected(i) then
				local id=browser:browserText(i)
				local pInfo=browserGraph[id]
				pInfo.material=w:menuText()
				pInfo:redraw() -- don't understand...
			end
		end
		updateScript()

	elseif(w:id()=="change source") then
		local browser=this:findWidget('clip board')
		for i=1,browser:browserSize() do
			if browser:browserSelected(i) then
				local id=browser:browserText(i)
				local pInfo=browserGraph[id]
				if (pInfo.scType == SceneComponent.ENTITY) then
					pInfo.source=w:menuText()
					pInfo:redraw()
				end
			end
		end
		updateScript()
	elseif(w:id()=="global operations") then
		local id= w:menuText()
		if (id=="save scene") then

			local default_folder= "../Resource/scripts/"
			local fn=Fltk.ChooseFile("Choose data",default_folder,"*.scn.lua", true)
			if fn then
				if string.sub(fn, -8)~='.scn.lua' then
					fn=fn..'.scn.lua'
				end
				local scene=browserGraphToTable()
				local sceneScript=table.toHumanReadableString(scene)

				--loadScene(scene)
				util.writeFile(fn, 'scene='..sceneScript..'\n'..loadSceneScript)
			end

		elseif(id=="load scene") then
			local default_folder="../Resource/scripts/"

			fn=Fltk.ChooseFile("Choose data",default_folder,"*.scn.lua")

			if not fn then
				return
			end
			local sceneScript=util.readFile(fn)
			local res,msg=loadstring(sceneScript)()
			if res then
				print(msg)
				dbg.console()
			end
			for i, v in ipairs(scene) do
				local info=SceneComponent(iupi)
				for k,vv in pairs(v) do
					info[k]=vv
				end
				addToBrowser(info)
			end
		elseif(id=="create plane") then
			local plane={}
			plane=SceneComponent(SceneComponent.PLANE)
			addToBrowser(plane)
		elseif(id=="create h11") then
			local entity={}
			entity=SceneComponent(SceneComponent.ENTITY)
			addToBrowser(entity)
		elseif(id=="create terrain") then
			local terrain={}
			terrain=SceneComponent(SceneComponent.TERRAIN)
			addToBrowser(terrain)
		end




	elseif (w:id()=="Run script") then

		local browser=this:findWidget('clip board')
		local _input=this:findWidget('script')
		for i=1,browser:browserSize() do
			if browser:browserSelected(i) then
				local id=browser:browserText(i)
				local pInfo=browserGraph[id]


				pos=pInfo.pos
				scale=pInfo.scale
				ori=pInfo.ori
				material=pInfo.material
				source=pInfo.source
				bCastShadow=pInfo.bCastShadow
				options=pInfo.options

				local f=_input:inputValue()
				local res,msg=loadstring(f)()

				--if res==nil then
				pInfo.material=material
				pInfo.source=source
				pInfo.bCastShadow=bCastShadow
				--pInfo.options:setValues(4000,4000,40,40)
				--end



				pInfo:redraw()
			end
		end


	elseif (w:id()=="clip board") then
		local browser=this:findWidget('clip board')
		for i=1,browser:browserSize() do
			if browser:browserSelected(i) then
				selectfunc(browser:browserText(i))
			else
				deselect(browser:browserText(i))
			end
		end
		updateScript()
	elseif (w:id()=="operations") then
		local op={}
		op=this:menuText()
		if op:left(6)=="rotate"then

		else

		end
	end




end


function drawIcon(editMode, cursorPos)
	if string.sub(editMode, 1,5)=='CLICK' then
		return 
	end
	local mat
	local thickness
	local pos=vector3N()
	if(editMode=='rotate') then
		thickness=50
		mat= "icons/refresh"
	else
		thickness=30
		mat= "icons/add"
	end
	pos:pushBack(cursorPos)

	mObjectList:registerObject('EDIT_MODE', 'QuadListY', mat, pos:matView(), thickness)
end

function handleEditingEvent(pushed,cur,ev,editMode)	

	local menu=this:findWidget("edit mode")

	if (ev=='PUSH') then
		drawIcon(editMode, pushed.cursorPos)
		menu:deactivate()
		bSnapToGrid=this:findWidget("snap to grid"):checkButtonValue()
		local browser=this:findWidget('clip board')
		for i=1,browser:browserSize() do
			if (browser:browserSelected(i)) then
				local graph=getInfo(browser, i)
				graph.push_state=copyInfo(graph)
			end
		end
		return 1
	elseif (ev=='DRAG') then
		if (editMode=='translate') then
			drawIcon(editMode, cur.cursorPos)
		end

		bSnapToGrid=this:findWidget("snap to grid"):checkButtonValue()
		local browser=this:findWidget('clip board')
		for i=1,browser:browserSize() do

			if (browser:browserSelected(i)) then
				local graph=getInfo(browser, i)
				local child=RE.ogreSceneManager():getSceneNode(graph.nodeId)

				if(editMode=='translate' or editMode=='translate Y') then
					local delta=cur.cursorPos-pushed.cursorPos

					if(editMode=='translate Y') then
						local amount=(pushed.y-cur.y)*1.0
						if(bSnapToGrid) then
							amount=(math.floor(amount/25.0))*25
						end
						delta=vector3(0,amount,0)
					else
						if(bSnapToGrid) then
							delta.x=(math.floor(delta.x/50.0))*50
							delta.y=0
							delta.z=(math.floor(delta.z/50.0))*50
						end
					end
					graph.pos:assign(graph.push_state.pos+delta)
					setTransform(child,graph)
				elseif (editMode=='rotate') then

					local amt=(pushed.x-cur.x)/-100.0

					if(bSnapToGrid) then
						amt=math.floor(amt/math.rad(15))*math.rad(15)
					end
					graph.ori:assign(quater(amt, vector3(0,1,0))*graph.push_state.ori)
					setTransform(child,graph)
				elseif (editMode=='scale') then
					local scale
					if(pushed.y-cur.y>0) then
						scale=1.0+(pushed.y-cur.y)/100.0
					else
						scale=1.0/(1.0+(cur.y-pushed.y)/100.0)
					end
					graph.scale:assign(graph.push_state.scale*scale)
					setTransform(child,graph)
				end
			end
		end
	elseif(ev=='RELEASE') then
		local browser=this:findWidget('clip board')
		for i=1,browser:browserSize() do
			if (browser:browserSelected(i)) then
				local graph=getInfo(browser, i)
				graph.push_state=nil
			end
		end
		mObjectList:erase("EDIT_MODE")
		menu:activate()
		updateScript()

		--this:findWidget("edit mode"):menuValue(0)
		this:redraw()
		return 1
	end
	return 0
end


function onFrameChanged(iframe)
end
function frameMove(fElapsedTime)
end
function deselectAll()
	local browser=this:findWidget('clip board')
	for i=1, browser:browserSize() do
		deselect(browser:browserText(i))
	end
	browser:browserDeselect()
	this:redraw();
end

loadSceneScript=[[
function loadScene(scene)
	local rootnode=RE.ogreRootSceneNode()
	local bgnode=RE.createChildSceneNode(rootnode,"backgroundNode")

	for i, info in ipairs(scene) do
		local nodeId=info.nodeId..'__'
		local pNode=RE.createChildSceneNode(bgnode, nodeId)
		if (info.scType==SceneComponent.PLANE) then
			if (info.options:size()==4) then
				entity=RE.createPlane("_entity_".. nodeId,
				info.options[0], info.options[1], info.options[2], info.options[3])
			else
				entity=RE.createPlane("_entity_"..nodeId,
				info.options[0], info.options[1], info.options[2], info.options[3], info.options[4], info.options[5])
			end
		elseif(info.scType==SceneComponent.ENTITY) then
			entity=RE.ogreSceneManager():createEntity("_entity_"..nodeId,info.source)
		else
			entity=RE.createTerrain("_entity_"..nodeId,info.source,info.options[0],info.options[1],info.options[2],info.options[3],info.options[4],info.options[5],info.options[6])
		end
		pNode:setPosition(info.pos.x,info.pos.y,info.pos.z)
		pNode:setOrientation(info.ori.w,info.ori.x,info.ori.y,info.ori.z)
		pNode:setScale(info.scale.x,info.scale.y,info.scale.z)

		if info.material~='' then
			entity:setMaterialName(info.material)
		end
		if not (info.bCastShadow) then
			entity:setCastShadows(false)
		end
		if(info.bNormaliseNormals) then
			entity:setNormaliseNormals(true)
		end

		pNode:attachObject(entity)
	end
	--bgnode:setPosition(100,0,0)
end
]]
