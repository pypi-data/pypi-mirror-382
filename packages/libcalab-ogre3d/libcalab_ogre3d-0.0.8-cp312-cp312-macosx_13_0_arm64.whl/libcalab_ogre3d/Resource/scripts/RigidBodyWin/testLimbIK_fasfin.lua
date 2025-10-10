require("config")
require("module")
require("common")

function ctor()
	this:create("Button", "button1");
	this:create("Button", "button2");
--	this:create("Value_Slider", "sliderx", "sliderx");
--	this:widget(0):sliderRange(0,0.5);
--	this:widget(0):sliderValue(0.1);
--	this:create("Value_Slider", "slidery", "slidery");
--	this:widget(0):sliderRange(0,0.5);
--	this:widget(0):sliderValue(0.1);
--	this:create("Value_Slider", "sliderz", "sliderz");
--	this:widget(0):sliderRange(-0.5,0.5);
--	this:widget(0):sliderValue(0.1);
	this:create("Value_Slider", "sliderlx", "sliderlx");
	this:widget(0):sliderRange(-200,200);
	this:widget(0):sliderValue(1);
	this:create("Value_Slider", "sliderly", "sliderly");
	this:widget(0):sliderRange(-200,200);
	this:widget(0):sliderValue(1);
	this:create("Value_Slider", "sliderlz", "sliderlz");
	this:widget(0):sliderRange(-200,200);
	this:widget(0):sliderValue(1);
	this:create("Value_Slider", "sliderrx", "sliderrx");
	this:widget(0):sliderRange(-200,200);
	this:widget(0):sliderValue(1);
	this:create("Value_Slider", "sliderry", "sliderry");
	this:widget(0):sliderRange(-200,200);
	this:widget(0):sliderValue(1);
	this:create("Value_Slider", "sliderrz", "sliderrz");
	this:widget(0):sliderRange(-200,200);
	this:widget(0):sliderValue(1);
	this:create("Check_Button", "optimize", "-optimize-")
	this:create("Value_Slider", "ValL", "ValL");
	this:widget(0):sliderRange(0.0,5.0);
	this:widget(0):sliderValue(1);
	this:create("Check_Button", "optiR", "optiRot")
	this:create("Value_Slider", "RotValM", "RotValM");
	this:widget(0):sliderRange(0.0,5.0);
	this:widget(0):sliderValue(0.3);
	this:create("Check_Button", "optiT", "optiTransl")
	this:create("Value_Slider", "TranslValN", "TranslValN");
	this:widget(0):sliderRange(0.0,2.0);
	this:widget(0):sliderValue(0.3);
	this:create("Check_Button", "iterik", "iterik")
	this:create("Value_Slider", "iterNum", "iterNum");
	this:widget(0):sliderRange(0,300);
	this:widget(0):sliderValue(10);

	this:updateLayout();
	this:updateLayout();

	config_manip={
		"../Resource/mocap_manipulation/bvh_files/gf_0515/2/gf_skel2-1.wrl",
		'../Resource/mocap_manipulation/bvh_files/gf_0515/2/gf_skel2-1.dof',
		"LeftElbow", "LeftWrist", vector3(0,0.0,0),
		"RightElbow", "RightWrist", vector3(0,0.0,0),
		reversed=true,
		skinScale=1,
	}

	config_gymnist={
		"../Resource/motion/gymnist/gymnist.wrl",
		'../Resource/motion/gymnist/gymnist.dof',
		'lradius', 'lhand', vector3(0,0,0),
		'rradius', 'rhand', vector3(0,0,0),
		reversed=false,
		skinScale=100,
	}
	config_gymnist_foot={
		"../Resource/motion/gymnist/gymnist.wrl",
		'../Resource/motion/gymnist/gymnist.dof',
		'ltibia', 'lfoot', vector3(0.000000,-0.053740,0.111624),
		'rtibia', 'rfoot', vector3(0.000000,-0.054795,0.112272),
		reversed=false,
		skinScale=100,
	}
	config_gymnist_hand={
		"../Resource/motion/gymnist/gymnist.wrl",
		'../Resource/motion/gymnist/gymnist.dof',
		'lradius', 'lhand', vector3(0.000000,-0.053740,0.111624),
		'rradius', 'rhand', vector3(0.000000,-0.054795,0.112272),
		reversed=true,
		skinScale=100,
	}
	config_run={
		"../Resource/motion/justin_straight_run/justin_straight_run.wrl",
		"../Resource/motion/justin_straight_run/justin_straight_run.dof", 
		'ltibia', 'lfoot', vector3(0.000000,-0.053740,0.111624),
		'rtibia', 'rfoot', vector3(0.000000,-0.054795,0.112272),
		reversed=false,
		skinScale=100,
	}

	--config=config_manip
	--config=config_run
	config=config_gymnist_foot
    mLoader=MainLib.VRMLloader (config[1])
	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, config[2])
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+0.07)
	end

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	local s=config.skinScale
	mSkin:scale(s,s,s); -- motion data often is in meter unit while visualization uses cm unit.
	mPose=vectorn()
	mPose:assign(mMotionDOF:row(0));
	mSkin:setPoseDOF(mPose);

	mEffectors=MotionUtil.Effectors()
	mEffectors:resize(2);
	lknee=mLoader:getBoneByName(config[3])
	mEffectors(0):init(mLoader:getBoneByName(config[4]), config[5])
	rknee=mLoader:getBoneByName(config[6]);
	mEffectors(1):init(mLoader:getBoneByName(config[7]), config[8])

	--mIK= MotionUtil.createFullbodyIkDOF_limbIK(mLoader.dofInfo, mEffectors, lknee, rknee, config.reversed);
	--mIK= MotionUtil.createFullbodyIk_MotionDOF_MultiTarget(mLoader.dofInfo, mEffectors);
	--mIK=MotionUtil.createFullbodyIkDOF_limbIK_straight(mLoader.dofInfo,mEffectors,lknee,rknee);
	
	if (config.reversed) then
		mIK=LimbIKsolver2(mLoader.dofInfo,mEffectors, CT.ivec(lknee:treeIndex(), rknee:treeIndex()), CT.vec(-1,-1))
	else
		mIK=LimbIKsolver2(mLoader.dofInfo,mEffectors, CT.ivec(lknee:treeIndex(), rknee:treeIndex()), CT.vec(1,1))
	end
	footPos=vector3N (2);
 	mIK:setOption(0)	
 	dbg.namedDraw("Sphere", vector3(0,0,0), "origin", "red")
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
	   local footOri=quaterN(2)
	   for i=0,1 do
		   local originalPos=mEffectors(i).bone:getFrame():toGlobalPos(mEffectors(i).localpos)
		   footPos(i):assign(originalPos);
		   footOri(i):assign(mEffectors(i).bone:getFrame().rotation)
		   dbg.namedDraw("Sphere", originalPos*config.skinScale, "x"..i)
	   end
	   footPos(1):radd(vector3(xx, yy,zz)/config.skinScale)
	   footPos(0):radd(vector3(rxx, ryy,rzz)/config.skinScale)
	   dbg.namedDraw("Sphere", footPos(0)*config.skinScale, "x0")
	   dbg.namedDraw("Sphere", footPos(1)*config.skinScale, "x1")
	   --mIK:IKsolve(mPose, footPos);
	   local importance=vectorn(2)
	   importance:setAllValue(1)
	   mIK:IKsolve3(mPose, MotionDOF.rootTransformation(mPose), footPos, footOri, importance)
	   --mIK:IKsolve3(mPose, MotionDOF.rootTransformation(mPose), footPos, footOri, importance)
	   mSkin:setPoseDOF(mPose);
	   ---mIK:IKsolve3(mPose, MotionDOF.rootTransformation(mPose), footPos, footOri, importance)
	  -- mSkin:setPoseDOF(mPose);
end

function onCallback(w, userData)  
	    xx= this:findWidget('sliderlx'):sliderValue()
	 	yy= this:findWidget('sliderly'):sliderValue()
	 	zz= this:findWidget('sliderlz'):sliderValue()
	 	rxx= this:findWidget('sliderrx'):sliderValue()
		ryy= this:findWidget('sliderry'):sliderValue()
		rzz= this:findWidget('sliderrz'):sliderValue()
		ValL = this:findWidget('ValL'):sliderValue()
		ValM = this:findWidget('RotValM'):sliderValue()
		ValN = this:findWidget('TranslValN'):sliderValue()
		iterNum = this:findWidget('iterNum'):sliderValue()
   if w:id()=="button1" then
	   print("button1\n");
   elseif w:id()=="button2" then
	   print("button2\n");
   elseif w:id()=="optiR" then
	   mIK:setOption(1)
	   limbik(w)
   elseif w:id()=="iterik" then
		mIK:setOption(2)
		limbik(w)
   elseif w:id()=="optiT" then
	   mIK:setOption(3)
	   limbik(w)
   elseif w:id()=="sliderlx"or w:id()=="sliderly"or w:id()=="sliderlz" or w:id()=="sliderrx" or w:id()=="iterNum"
	   or w:id()=="sliderry"or w:id()=="sliderrz" or w:id()=="ValL" or w:id()== "RotValM" or w:id()=="TranslValN"then
--xx= this:findWidget('sliderlx'):sliderValue()
--	 	yy= this:findWidget('sliderly'):sliderValue()
--	 	zz= this:findWidget('sliderlz'):sliderValue()
--	 	rxx= this:findWidget('sliderrx'):sliderValue()
--		ryy= this:findWidget('sliderry'):sliderValue()
--		rzz= this:findWidget('sliderrz'):sliderValue()
		limbik(w)
   end
end

function dtor()
end

function frameMove(fElapsedTime)
end
