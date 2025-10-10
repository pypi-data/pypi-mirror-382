require("config")
require("module")
require("common")

-- moduleIk.lua contains the actual contructors of the IK solvers.
require("moduleIK")

config_hanyang={
	"../Resource/motion/MOB1/hanyang_lowdof_T.wrl",
	"../Resource/motion/MOB1/hanyang_lowdof_T_MOB1_Run_F_Loop.fbx.dof" ,
	{
		-- hands
		{'LeftKnee', 'LeftAnkle', vector3(0, -0.06, 0.08), reversed=false},
		{'RightKnee', 'RightAnkle', vector3(0, -0.06, 0.08), reversed=false},
	},
	skinScale=100,
}

config=config_hanyang

function ctor()
	this:create("Button", "rotate light", "rotate light",1)

	this:create("Check_Button", "use knee damping", "use knee damping")
	this:widget(0):checkButtonValue(true)
	
	--dbg.console();
	--mMot=loadMotion(config[1], config[2])
	mLoader=MainLib.VRMLloader(config[1])

	mLoader:removeAllRedundantBones()
	mLoader:_initDOFinfo()

	-- rendering is done in cm scale
	local drawSkeleton=false -- draw skeleton is slow on m1 mac.
	mSkin= RE.createVRMLskin(mLoader, false);
	mSkin:setMaterial("lightgrey_transparent")
	local s=config.skinScale
	mSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mSkin:setThickness(3/s)
	mPose=vectorn()
	mLoader:updateInitialBone()
	mLoader:getPoseDOF(mPose)

	this:updateLayout()
	local initialHeight=1.0
	mPose:set(1, initialHeight)

	mPose0=mPose:copy()

	mSkin:setPoseDOF(mPose);

	mSolverInfo=createIKsolver(solvers.LimbIKsolver, mLoader, config[3]) -- defined in moduleIK
	local numCon=mSolverInfo.numCon
	mIK=mSolverInfo.solver

	footPos=vector3N (numCon);

	mLoader:setPoseDOF(mPose)
	local effectors=mSolverInfo.effectors
	originalPos={}
	for i=0,numCon-1 do
		local opos=effectors(i).bone:getFrame():toGlobalPos(effectors(i).localpos)
		originalPos[i+1]={opos, effectors(i).bone:getFrame().rotation:copy()}
	end

	g_phase=0
end

-- 
function swingMap(_phase, midPos)
	assert(_phase>-0.001)
	assert(_phase<1.001)
	local gamma=1.26 --walk
	--local gamma=1.13 --slow run
	local phase=math.pow(_phase, gamma)
	--
	local wy=(phase-0.5)*2.0

	local y=(1.0-wy*wy)*midPos.y
	local x=0
	local z=0

	return vector3(x,y,z)
end
function limbik(phase)

	local phases
	if phase<1 then
		-- L swing
		phases={phase, 0}
	else
		-- R swing
		phases={0, phase-1}
	end
	-- to see output, press ctrl+alt+o
	-- on m1 mac. output font is small so use ctrl+c (screen capture). the images will show readable text
	RE.output2("phase", phase, table.toPrettyString(phases))

	mPose:assign(mPose0)

	local numCon=mSolverInfo.numCon
	local footOri=quaterN(numCon)
	for i=0,numCon-1 do
		local opos=originalPos[i+1]
		footPos(i):assign(opos[1]+swingMap(phases[i+1], vector3(0,0.1,0)));
		footOri(i):assign(opos[2])
	end

	local importance=vectorn(numCon)
	importance:setAllValue(1)
	
	local roottf=MotionDOF.rootTransformation(mPose)
	roottf.translation:radd(vector3(-math.sin(phase*math.pi)*0.02,0,0))
	mIK:IKsolve3(mPose, roottf, footPos, footOri, importance)
	mSkin:setPoseDOF(mPose);
end

function onCallback(w, userData)  
	if w:id()=="use knee damping" then
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
	local phaseVel=1
	g_phase=g_phase+fElapsedTime*phaseVel
	if g_phase>2 then
		g_phase=0
	end

	local phase=g_phase

	limbik(phase)

end

function handleRendererEvent(ev, button, x,y) 
	return 0
end
