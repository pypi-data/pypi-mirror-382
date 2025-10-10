
require("config")

require("common")
require("subRoutines/RagdollSim")
require("subRoutines/Timeline")
--[[ parameters ]]--

useCapturedInitialPose=false
useCase={}

--model=model_files.hyunwoo_fourDOF3
--model=model_files.lowerbody useCapturedInitialPose=false
--model=model_files.lowerbody_allDOF1 useCapturedInitialPose=false
--model=model_files.lowerbody_elastic useCapturedInitialPose=false
--model=model_files.lowerbody_elastic useCapturedInitialPose=false
--model=model_files.jump5_cart
--model=model_files.hyunwoo_real useCapturedInitialPose=false
--model=model_files.cart_pole
--model=model_files.hyunwoo_real_cart
--model=model_files.hyunwoo_full_cart 
--model=model_files.hyunwoo_ball_cart
--model=model_files.justin_straight_run model.initialHeight=model.initialHeight+0.3
--model=model_files.justin_jump model.initialHeight=model.initialHeight-0.05 viewRotate=90
model=model_files.gymnist model.initialHeight=0.07 model.k_p_PD=500 model.k_d_PD=5


timestep=1/8000
rendering_step=1/30
--rendering_step=timestep -- only for debugging

simulationMode=SimulationMode.TrackMotion

integrator=Physics.DynamicsSimulator.EULER
--integrator=Physics.DynamicsSimulator.RUNGE_KUTTA 
--simulator=simulators.VP     -- 8~18ms (RK4: 13~24ms)
--simulator=simulators.gmbs   -- 24~34ms useInverseDynamics: 35~47ms (gmbs)-> 9~19ms (gmbs2- cool!) 
simulator=simulators.TRL_penalty 
--simulator=simulators.SDFAST -- (RK4:15~35ms)
--simulator=simulators.AIST     -- 6~16ms (RK4:12~22ms) useInverseDynamics: 17~28 (RK4:22~35ms) (gmbs) 17~28ms (vp)
--simulator=simulators.UT     -- 40~47ms (RK4:118~130ms)
ServoMethods={PD=1, HD=2, QP=3}
--servoMethod=ServoMethods.QP
servoMethod=ServoMethods.PD


if EventReceiver then
	--class 'EVR'(EventReceiver)
	EVR=LUAclass(EventReceiver)
	function EVR:__init(graph)
		--EventReceiver.__init(self)
		self.currFrame=0
		self.cameraInfo={}
	end
end
function init_globals()
	usePenaltyMethod=true
	collisionTestOnlyAnkle=false

	manualAdjust=false
	debugContactParam={10, 0, 0.01, 0, 0}-- size, tx, ty, tz, tfront
	--[[ implementations ]]--
	if servoMethod==ServoMethods.HD then
		useInverseDynamics=true
		useQPsolver=false
	elseif servoMethod==ServoMethods.QP then
		useInverseDynamics=false
		usePenaltyMethod=false
		useQPsolver=true
	elseif servoMethod==ServoMethods.PD then
		usePenaltyMethod=true
	end

	if useInverseDynamics==true then
		usePenaltyMethod=true
	end

	initialHeight=model.initialHeight

	model.penaltyForceStiffness=30000
	model.penaltyForceDamp=3000
	k_p=model.k_p_PD	-- Nm/rad
	k_d=model.k_d_PD --  Nms/rad. worked in range [0, 1]
	model.k_scale_active_pd.hip={3,1,1}
	model.k_scale_active_pd.knee={1,1,1}
	model.k_scale_active_pd.chest={3,1,1}
	if not useCapturedInitialPose then
		initialHeight=initialHeight+1.2
	end

	niter=math.floor(rendering_step/timestep+0.5)
end

function ctor()
	init_globals()
   --	this:create("Button", "Start", "Start")
   --	this:widget(0):buttonShortcut("FL_ALT+s")

   --this:create("Check_Button", "simulation", "simulation", 0, 2,0)
   --this:widget(0):checkButtonValue(1) -- 1 for imediate start
   --this:widget(0):buttonShortcut("FL_CTRL+s")
   
   this:create("Button", "single step", "single step", 2, 3,0)
   
   this:create("Check_Button", "draw skeleton", "draw skeleton", 0, 3,0)
   this:widget(0):checkButtonValue(0)

   this:updateLayout()
   this:redraw()
   
   --RE.viewpoint().vpos:assign(vector3(330.411743, 69.357635, 0.490963))
   --RE.viewpoint().vat:assign(vector3(-0.554537, 108.757057, 0.477768))
   --RE.viewpoint():update()
   --RE.viewpoint():TurnRight(math.rad(viewRotate or 0))
   _start()
end

function dtor()
   -- remove objects that are owned by C++
   if mSkin~=nill then
      RE.remove(mSkin)
      mSkin=nil
   end
   if mSkin2~=nill then
      RE.remove(mSkin2)
      mSkin2=nil
   end
   if mTimeline then
	   mTimeline:dtor()
       mTimeline=nil
   end
   mEventReceiver=nil
   -- remove objects that are owned by LUA
   collectgarbage()
end

function _start()
   dtor()
	mEventReceiver=EVR()
	mTimeline=Timeline("Timeline", 1000000, 1/30)
   print("start")
   mLoader=MainLib.VRMLloader(model.file_name)
   mLoader:printHierarchy()
   MotionLoader.setVoca(mLoader, model.bones)
   if useCapturedInitialPose and model.mot_file~=nill then

	   local container=MotionDOFcontainer(mLoader.dofInfo, model.mot_file)
	   mMotionDOF=container.mot
   else

	   local container=MotionDOFcontainer(mLoader.dofInfo)
	   local numFrames=3000
	   container:resize(numFrames)
	   for i=0, container:numFrames()-1 do
		   container.mot:row(i):setAllValue(0)
	   end
	   container.mot:matView():column(3):setAllValue(1) --quaternion
	   --dbg.console()
	   mMotionDOF=container.mot
   end
   mFloor=MainLib.VRMLloader("../Resource/mesh/floor_y.wrl")

	
   
   drawSkeleton=this:findWidget("draw skeleton"):checkButtonValue()
   
   mRagdoll= RagdollSim(mLoader, drawSkeleton, mMotionDOF)
   mRagdoll.drawDebugInformation=true

   mSkin2=RE.createVRMLskin(mFloor, false)
   mSkin2:scale(100,100,100)

   

end

function onCallback(w, userData)
   if w:id()=="Start" then
      _start()
   end
end

theta=vectorn()

print("niter= ",niter)
function frameMove(fElapsedTime)
end

function EVR:onFrameChanged(win, iframe)
   if mLoader~=nill then --and this:findWidget("simulation"):checkButtonValue() then
      
	   mRagdoll:frameMove(niter)
   end
end
function handleRendererEvent(ev, x,y)
	return 0
end
