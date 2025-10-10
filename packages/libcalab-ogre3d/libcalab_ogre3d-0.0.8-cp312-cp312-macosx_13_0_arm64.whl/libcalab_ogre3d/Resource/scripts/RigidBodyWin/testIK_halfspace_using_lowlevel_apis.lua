-- This example doesn't use IK solver. Instead, it directly uses jacobians and optimizers.
-- diff with ./testIK_halfspace.lua
require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")
local LBFGS_opta=require("subRoutines/OptimizerLBFGS")

local IKsolver=LUAclass()

function IKsolver:__init(loader) 
	self.loader=loader
	self._effectors_unused=MotionUtil.Effectors()
	self._con_unused=MotionUtil.Constraints()
	-- option: euler_root=true
	self.loaderToTree=MotionUtil.LoaderToTree(loader, self._effectors_unused, self._con_unused, true, false)

	local ndof=self.loaderToTree:nDOF()
	self.x_original=vectorn(ndof)
	self.constraints={}
end
function IKsolver:clearConstraints()
	self.constraints={}
end
function IKsolver:IKsolve(initialPose)
	local loaderToTree=self.loaderToTree
	loaderToTree:setPoseDOF(self.loader.dofInfo, initialPose)
	loaderToTree:getQ(self.x_original)

	local x_orig=self.x_original
	local ndof=self.loaderToTree:nDOF()
	local h=LBFGS_opta(ndof, 1e-8, 0,0)

	do
		-- damping terms
		local w=0.01
		for j=0, ndof-1 do
			-- add objective to minimize 1*x_j - x_orig_j
			h:addWeighted(w, 1, j , -1*x_orig(j))
		end
	end

	h.opt=self
	h.customGradientFunction=function (self, pos, grad)
		local loaderToTree=self.opt.loaderToTree
		loaderToTree:setQ(pos)
		local loader=self.opt.loader
		local ndof=loaderToTree:nDOF()

		local cost=0
		for icon, conInfo in ipairs(self.opt.constraints) do

			if conInfo[1]=='Effector' then
				local w=1
				local _, bone, localpos, targetpos=unpack(conInfo)

				local gpos=loaderToTree:globalFrame(bone:treeIndex())*localpos
				local deltaS=targetpos-gpos
				cost=cost+deltaS:dotProduct(deltaS)*w
				loaderToTree:updateGrad_S_JT(grad, -2.0*w*deltaS, bone:treeIndex(), localpos)
			elseif conInfo[1]=='HalfSpace' then
				local w=1
				local _, bone, localpos, plane=unpack(conInfo)
				local tf=loaderToTree:globalFrame(bone:treeIndex())
				local d=plane:distance(tf*localpos) 
				if d>0 then
					cost=cost+d*d*w
					loaderToTree:updateGrad_S_JT(grad, w*(2.0*d)*plane.normal,bone:treeIndex(), localpos)
				end
			end
		end
		return cost
	end
	print('started solving')
	local timer=util.Timer()
	local res= h:solve(self.x_original)
	--local res=self.x_original
	print('solved (s):', timer:stop2()/1e6)

	loaderToTree:setQ(res)
	-- the input pose will be changed
	loaderToTree:getPoseDOF(self.loader.dofInfo,initialPose)
end

function IKsolver:addEffectorConstraint(bone, localpos, targetPos)
	local con={'Effector', bone, localpos, targetPos}
	table.insert(self.constraints, con)
end
function IKsolver:addHalfSpaceConstraint(bone, localpos, plane)
	local con={'HalfSpace', bone, localpos, plane}
	table.insert(self.constraints, con)
end

config_hyunwoo={
	"../Resource/motion/locomotion_hyunwoo/hyunwoo_lowdof_T.wrl",
	"../Resource/motion/locomotion_hyunwoo/hyunwoo_lowdof_T_locomotion_hl.dof",
	{
		{'LeftKnee', 'LeftAnkle', vector3(0, -0.06, 0.08), reversed=false},
		{'RightKnee', 'RightAnkle', vector3(0, -0.06, 0.08), reversed=false},
	},
	skinScale=100,
}


config=config_hyunwoo


function eventFunction()
	limbik()
end
function createIKsolver(solverType, loader, config)
	local out={}
	local mEffectors=MotionUtil.Effectors()
	local numCon=#config
	mEffectors:resize(numCon);
	out.effectors=mEffectors
	out.numCon=numCon

	for i=0, numCon-1 do
		local conInfo=config[i+1]
		local kneeInfo=1
		local lknee=loader:getBoneByName(conInfo[kneeInfo])
		mEffectors(i):init(loader:getBoneByName(conInfo[kneeInfo+1]), conInfo[kneeInfo+2])
	end
	out.solver=IKsolver(loader);
	return out
end

function loadMotion(skel, motion, skinScale)
	local mot={}
	mot.loader=MainLib.VRMLloader (skel)
	mot.motionDOFcontainer=MotionDOFcontainer(mot.loader.dofInfo, motion)
	if skinScale then
		mot.skin=createSkin(skel, mot.loader, skinScale)
		mot.skin:applyMotionDOF(mot.motionDOFcontainer.mot)
		mot.skin:setMaterial('lightgrey_transparent')
	end
	return mot
end

function ctor()
	if true then
		RE.renderer():viewport():setOrthographicMode(true)
		RE.ogreSceneManager():setFog( 0.77,0.92,1, 0.0,2800, 3800 )
		RE.viewpoint():setFOVy(45.000000)
		RE.viewpoint():setZoom(2.325926)
		RE.viewpoint().vpos:set(99.786073, 99.692761, 1454.864508)
		RE.viewpoint().vat:set(83.798100, 78.122854, -0.909899)
		RE.viewpoint():update()
	end

	this:create("Button", "rotate light", "rotate light",1)
	this:create("Value_Slider", "arm ori y", "arm ori y",1)
	this:widget(0):sliderRange(-math.rad(90),math.rad(90))
	this:widget(0):sliderValue(0)
	this:create("Value_Slider", "normal", "normal",1)
	this:widget(0):sliderRange(-math.rad(90),math.rad(90))
	this:widget(0):sliderValue(-math.rad(10))
	this:create("Value_Slider", "normal2", "normal2",1)
	this:widget(0):sliderRange(-math.rad(90),math.rad(90))
	this:widget(0):sliderValue(math.rad(10))
	

	this:updateLayout();

	--dbg.console();
	mMot=loadMotion(config[1], config[2])
	mLoader=mMot.loader

	--local max_iter=mLoader:numBone()
	for i=1, mLoader:numBone()-1 do
		if mLoader:VRMLbone(i):numChannels()==0 then
			mLoader:removeAllRedundantBones()
			--mLoader:removeBone(mLoader:VRMLbone(i))
			--mLoader:export(config[1]..'_removed_fixed.wrl')
			break
		end
	end
	mLoader:_initDOFinfo()


	mMotionDOFcontainer=mMot.motionDOFcontainer
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+(config.initialHeight or 0))
	end

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, true);
	mSkin:setMaterial("lightgrey_transparent")
	local s=config.skinScale
	mSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mSkin:setThickness(3/s)
	mPose=vectorn()
	mPose:assign(mMotionDOF:row(0));
	mSkin:setPoseDOF(mPose);


	mSolverInfo=createIKsolver(solver, mLoader, config[3])
	mEffectors=mSolverInfo.effectors
	numCon=mSolverInfo.numCon
	mIK=mSolverInfo.solver

	footPos=vector3N (numCon);

	mLoader:setPoseDOF(mPose)
	local originalPos={}
	for i=0,numCon-1 do
		local opos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		originalPos[i+1]=opos*config.skinScale
	end
	table.insert(originalPos, mLoader:bone(1):getFrame().translation*config.skinScale) --  half-space position
	table.insert(originalPos, mLoader:bone(1):getFrame().translation*config.skinScale+vector3(100,0,0)) --  half-space position

	mCON=Constraints(unpack(originalPos))
	--mCON:setOption(1*config.skinScale)
	mCON:connect(eventFunction)

	limbik()
end
function limbik()
	mPose:assign(mMotionDOF:row(0));
	mLoader:setPoseDOF(mPose);
	local hasHalfspace=1
	local planeCenter=mCON.conPos(2)/config.skinScale
	local planeCenter2=mCON.conPos(3)/config.skinScale
	mIK:clearConstraints()
	-- local pos to global pos
	for i=0,numCon-1 do
		local originalPos=mCON.conPos(i)/config.skinScale
		mIK:addEffectorConstraint(mEffectors(i).bone, mEffectors(i).localpos, originalPos)
	end
	
	local bone1=mLoader:getBoneByName('LeftElbow')
	local lpos1=vector3(0.24,0,0)
	if hasHalfspace==1 then

		do
			-- the first half-space
			local w=1
			local normalQ=quater(this:findWidget('normal'):sliderValue(),vector3(0,0,1))
			local normal=normalQ*vector3(0,1,0)
			local plane=Plane(normal, planeCenter)
			dbg.draw("Box", transf(normalQ, planeCenter), 'box', vector3(3,0,3), 100, 'blue_transparent')
			dbg.draw("ArrowM", planeCenter, planeCenter+normal*0.3, 'normal', 0.05)
			mIK:addHalfSpaceConstraint( bone1, lpos1, plane)
		end

		do 
			local w=1
			local normalQ2=quater(this:findWidget('normal2'):sliderValue(),vector3(0,0,1))
			local normal2=normalQ2*vector3(0,1,0)
			local plane=Plane(normal2, planeCenter2)
			dbg.draw("Box", transf(normalQ2, planeCenter2), 'box2', vector3(3,0,3), 100, 'blue_transparent')
			dbg.draw("ArrowM", planeCenter2, planeCenter2+normal2*0.3, 'normal2', 0.05)
			mIK:addHalfSpaceConstraint( bone1, lpos1, plane)
		end
	end

	mIK:IKsolve(mPose)
	mSkin:setPoseDOF(mPose);

	if hasHalfspace==1 then
		dbg.draw("SphereM", mSkin:getState():globalFrame(bone1:treeIndex()):toGlobalPos(lpos1), 'conWrist', "red", 0.05)
	end
end

function onCallback(w, userData)  

	if w:id()=="button1" then
		print("button1\n");
	  elseif w:id()=='rotate light' then
	  local osm=RE.ogreSceneManager()
	  if osm:hasSceneNode("LightNode") then
		  local lightnode=osm:getSceneNode("LightNode")
		  lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
	  end
	end
	limbik()
end

function dtor()
end

function frameMove(fElapsedTime)
end

function handleRendererEvent(ev, button, x,y) 
	if mCON then
		return mCON:handleRendererEvent(ev, button, x,y)
	end
	return 0
end
