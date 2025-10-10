require("config")
require("module")
require("common")
require("RigidBodyWin/subRoutines/Constraints")

-- moduleIk.lua contains the actual contructors of the IK solvers.
require("moduleIK")

config_gymnist_hand={
	"../Resource/motion/gymnist/gymnist.wrl",
	'../Resource/motion/gymnist/gymnist.dof',
	{
		{'lradius', 'lhand', vector3(0,0,0), reversed=true},
		{'rradius', 'rhand', vector3(0,0,0), reversed=true},
	},
	skinScale=100,
}

config_run={
	"../Resource/motion/justin_straight_run/justin_straight_run.wrl",
	"../Resource/motion/justin_straight_run/justin_straight_run.dof", 
	{
		{'ltibia', 'lfoot', vector3(0.000000,-0.053740,0.111624),},
		{'rtibia', 'rfoot', vector3(0.000000,-0.054795,0.112272),},
	},
	skinScale=100,
}
config_jump={
	"../Resource/motion/justin_jump.wrl",
	"../Resource/motion/justin_jump.dof", 
	{
		{'ltibia', 'lfoot', vector3(0.000000,-0.053740,0.111624),},
		{'rtibia', 'rfoot', vector3(0.000000,-0.054795,0.112272),},
	},
	skinScale=100,
}
config_hyunwoo={
	"../Resource/motion/locomotion_hyunwoo/hyunwoo_lowdof_T2.wrl",
	"../Resource/motion/locomotion_hyunwoo/hyunwoo_lowdof_T_locomotion_hl.dof",
	{
		{'LeftKnee', 'LeftAnkle', vector3(0, -0.06, 0.08), reversed=false},
		{'RightKnee', 'RightAnkle', vector3(0, -0.06, 0.08), reversed=false},
	},
	skinScale=100,
}
config_hanyang={
	"../Resource/motion/MOB1/hanyang_lowdof_T.wrl",
	"../Resource/motion/MOB1/hanyang_lowdof_T_MOB1_Run_F_Loop.fbx.dof" ,
	{
		-- hands
		{'LeftElbow', 'LeftWrist', vector3(0.05, 0, 0), reversed=true},
		{'RightElbow', 'RightWrist', vector3(-0.05, 0, 0), reversed=true},
	},
	skinScale=100,
}

config_gymnist_all={
	"../Resource/motion/gymnist/gymnist.wrl",
	'../Resource/motion/gymnist/gymnist.dof',
	{ 
		{'lfemur', 'ltibia', 'lfoot', vector3(0.000000,-0.053740,0.111624)},
		{'rfemur', 'rtibia', 'rfoot', vector3(0.000000,-0.054795,0.112272)},
		{'lhumerus', 'lradius', 'lhand', vector3(0.000000,-0.053740,0.111624), reversed=true},
		{'rhumerus', 'rradius', 'rhand', vector3(0.000000,-0.054795,0.112272), reversed=true},
		--{'ltibia', 'lfoot', vector3(0.000000,-0.053740,0.111624)},
		--{'rtibia', 'rfoot', vector3(0.000000,-0.054795,0.112272)},
		--{ 'lradius', 'lhand', vector3(0.000000,-0.053740,0.111624), reversed=true},
		--{ 'rradius', 'rhand', vector3(0.000000,-0.054795,0.112272), reversed=true},
	},
	skinScale=100,
	initialHeight=0.07,
}

config_ETRI={
	"../Resource/motion/skeletonEditor/fitting2_1dof_fixed.wrl",
	"../Samples/scripts/RigidBodyWin/retargetting/data/Data/2_1.bvh.dof.bvh",
	--{ 
	--	{'RHip', 'RKnee', 'RAnkle', vector3(7.1624,-2.3740,0), reversed=true},
	--	{'LHip', 'LKnee', 'LAnkle', vector3(7.2272,-2.4795,0), reversed=true},
	--	{'RShoulder', 'RElbow', 'RWrist', vector3(0.000000,-0.053740,0.111624), reversed=false},
	--	{'LShoulder', 'LElbow', 'LWrist', vector3(0.000000,-0.054795,0.112272), reversed=false},
	--},
	{ 
		{'RHip', 'RKnee', 'RAnkle', vector3(0,0,0), reversed=true},
		{'LHip', 'LKnee', 'LAnkle', vector3(0,0,0), reversed=true},
		{'RShoulder', 'RElbow', 'RWrist', vector3(0.000000,0,0), reversed=false},
		{'LShoulder', 'LElbow', 'LWrist', vector3(0.000000,0,0), reversed=false},
	},
	skinScale=2.54,
}

config_Jun={
	"../Resource/Jun/humanHanyang/humanHanyang.wrl",
	"../Resource/Jun/MoleculeMotion/gf150212/gfMotion.bvh.dof",
	{ 
		{'RightHip', 'RightKnee', 'RightAnkle', vector3(0,0,0), reversed=true},
		{'LeftHip', 'LeftKnee', 'LeftAnkle', vector3(0,0,0), reversed=true},
		{'RightShoulder', 'RightElbow', 'RightWrist', vector3(0,0,0), reversed=false},
		{'LeftShoulder', 'LeftElbow', 'LeftWrist', vector3(0,0,0), reversed=false},
	},
	skinScale=100,
	initialHeight=-0.025,
}

--config=config_gymnist_all
--config=config_gymnist_hand
config=config_hyunwoo
--config=config_hanyang
--config=config_ETRI
--config=config_Jun
--config=config_jump

--solver=solvers.LimbIKsolver
--solver=solvers.LimbIKsolverHybrid
--solver=solvers.MultiTarget
solver=solvers.MultiTarget_lbfgs

selectedSolvers={
	solvers.MultiTarget_lbfgs,
	solvers.LimbIKsolver,
	solvers.LimbIKsolver2,
}

function eventFunction()
	limbik()
end


function ctor()
	this:create("Button", "rotate light", "rotate light",1)
	
	this:create("Choice", "choose IK solver")
	do
		this:widget(0):menuSize(#selectedSolvers+1)
		this:widget(0):menuItem(0,"choose IK solver")
		for i,v in ipairs(selectedSolvers) do
			this:widget(0):menuItem(i,table.findKey(solvers, v))
		end
		this:widget(0):menuValue(1)
	end

	this:create("Check_Button", "use knee damping", "use knee damping")
	this:widget(0):checkButtonValue(true)
	
	this:create("Value_Slider", "impor0", "impor0");
	this:widget(0):sliderRange(0,1);
	this:widget(0):sliderValue(1);
	this:create("Value_Slider", "impor1", "impor1");
	this:widget(0):sliderRange(0,1);
	this:widget(0):sliderValue(1);
	this:create("Value_Slider", "impor2", "impor2");
	this:widget(0):sliderRange(0,1);
	this:widget(0):sliderValue(1);
	this:create("Value_Slider", "impor3", "impor3");
	this:widget(0):sliderRange(0,1);
	this:widget(0):sliderValue(1);


	this:addText("below options are only \nfor the LimbIKsolver2.")
	ValL=100
	ValM=30
	ValN=10
	this:create("Value_Slider", "ValL", "ValL");
	this:widget(0):sliderRange(0.0,100.0);
	this:widget(0):sliderValue(ValL);
	this:create("Check_Button", "optiR", "optiRot")
	this:widget(0):checkButtonValue(1)
	this:create("Value_Slider", "RotValM", "RotValM");
	this:widget(0):sliderRange(0.0,50.0);
	this:widget(0):sliderValue(ValM);
	this:create("Check_Button", "optiT", "optiTransl")
	this:widget(0):checkButtonValue(1)
	this:create("Value_Slider", "TranslValN", "TranslValN");
	this:widget(0):sliderRange(0.0,200.0);
	this:widget(0):sliderValue(ValN);
	this:create("Check_Button", "iterik", "iterik")
	this:widget(0):checkButtonValue(1)
	iterNum=10
	this:create("Value_Slider", "iterNum", "iterNum");
	this:widget(0):sliderRange(0,300);
	this:widget(0):sliderValue(iterNum);
	this:updateLayout();
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
	kneeIndex=mSolverInfo.kneeIndex
	axis=mSolverInfo.axis
	mIK=mSolverInfo.solver

	footPos=vector3N (numCon);

	mLoader:setPoseDOF(mPose)
	local originalPos={}
	for i=0,numCon-1 do
		local opos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		originalPos[i+1]=opos*config.skinScale
	end
	mCON=Constraints(unpack(originalPos))
	--mCON:setOption(1*config.skinScale)
	mCON:connect(eventFunction)
end
function limbik()
	mPose:assign(mMotionDOF:row(0));
	mLoader:setPoseDOF(mPose);
	-- local pos to global pos
	ValL = this:findWidget('ValL'):sliderValue()
	ValM = this:findWidget('RotValM'):sliderValue()
	ValN = this:findWidget('TranslValN'):sliderValue()
	iterNum = this:findWidget('iterNum'):sliderValue()
	mIK:setValue(ValL,ValM,ValN,iterNum)
	local footOri=quaterN(numCon)
	for i=0,numCon-1 do
		--local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		local originalPos=mCON.conPos(i)/config.skinScale
		footPos(i):assign(originalPos);
		footOri(i):assign(mEffectors(i).bone:getFrame().rotation)
		--dbg.namedDraw("Sphere", originalPos*config.skinScale, "x"..i)
	end
	local importance=vectorn(numCon)
	--importance:setAllValue(1)
	impor0 = this:findWidget('impor0'):sliderValue()
	impor1 = this:findWidget('impor1'):sliderValue()
	impor2 = this:findWidget('impor2'):sliderValue()
	impor3 = this:findWidget('impor3'):sliderValue()
	importance:setValues(impor0,impor1,impor2,impor3)
	ValN = this:findWidget('TranslValN'):sliderValue()
	
	if mIK.IKsolve3 then
		--dbg.console();
		mIK:IKsolve3(mPose, MotionDOF.rootTransformation(mPose), footPos, footOri, importance)
	else
	
		mIK:IKsolve(mPose, footPos)
	end
	--mIK:IKsolve3(mPose, MotionDOF.rootTransformation(mPose), footPos, footOri, importance)
	mSkin:setPoseDOF(mPose);
	---mIK:IKsolve3(mPose, MotionDOF.rootTransformation(mPose), footPos, footOri, importance)
	-- mSkin:setPoseDOF(mPose);
end

function onCallback(w, userData)  

	iterNum = this:findWidget('iterNum'):sliderValue()
	if w:id()=="button1" then
		print("button1\n");
	  elseif w:id()=='rotate light' then
	  local osm=RE.ogreSceneManager()
	  if osm:hasSceneNode("LightNode") then
		  local lightnode=osm:getSceneNode("LightNode")
		  lightnode:rotate(quater(math.rad(30), vector3(0,1,0)))
	  end
	  elseif w:id()=="choose IK solver" then
		  local v=w:menuValue()
		  if v~=0 then
			  solver=selectedSolvers[v]
			  mIK=_createIKsolver(solver,mLoader,mEffectors, kneeIndex, axis,mSolverInfo._hipIndex)
		  end
	elseif w:id()=="optiR" or w:id()=="iterik" or w:id()=="optiT" then
		local id=w:id()
		if w:checkButtonValue() then
			mIK:setOption(id, 1)
		else
			mIK:setOption(id, 0)
		end
		limbik(w)
	elseif string.sub(w:id(),1,6)=="slider" then
		limbik(w)
	elseif w:id()=="use knee damping" then
		if w:checkButtonValue() then
			mIK:setOption("useKneeDamping", 1)
		else
			mIK:setOption("useKneeDamping", 0)
		end
	end
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
