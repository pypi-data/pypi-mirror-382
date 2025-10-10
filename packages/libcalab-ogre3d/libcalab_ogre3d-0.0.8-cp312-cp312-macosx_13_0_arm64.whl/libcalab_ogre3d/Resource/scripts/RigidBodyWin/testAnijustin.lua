require("config")
require("module")
require("common")

function ctor()
--	this:create("Button", "button1", "button1");
--	this:create("Value_Slider", "slidery", "slidery");
--	this:widget(0):sliderRange(0,0.5);
--	this:widget(0):sliderValue(0.1);
--	this:updateLayout();

	mLoader=MainLib.VRMLloader ("../Resource/motion/justin_straight_run/justin_straight_run.wrl")

	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, '../Resource/motion/justin_straight_run/justin_straight_run.dof')
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+0.07)
	end

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	mSkin:scale(100,100,100); -- motion data is in meter unit while visualization uses cm unit.
	mSkin:setPoseDOF(mMotionDOF:row(0));

--	mGraph={}
--	mGraph.start={644, 821, next='walk'}
--	mGraph.walk={821, 972, next='walk'}
--
--	for v, seg in pairs(mGraph) do
--		seg.mot=mMotionDOF:range(seg[1], seg[2]):copy()
--	end
--	
--	mCurrSeg=mGraph.start
--	mMotion=mCurrSeg.mot
--	mDelta=0
--	mTime=0
--	mNewMotion=MotionDOF(mLoader.dofInfo)
	
--	mNewMotion:stitch(mGraph.start.mot, mGraph.walk.mot)
--	mNewMotion2=MotionDOF(mLoader.dofInfo)
--	mNewMotion2:stitch(mNewMotion, mGraph.walk.mot)

	mSkin:applyMotionDOF(mMotionDOF)
	RE.motionPanel():motionWin():addSkin(mSkin)
	print('ctor')
end
function frameMove()
--function frameMove(fElapsedTime)
--  mTime=mTime+fElapsedTime
-- 	print(mTime)
-- 	local currFrame=math.round(mTime*120)
-- 	local lookAhead=20
-- 	if mMotion:numFrames()<currFrame+lookAhead then
-- 		local prevMotion=mMotion
-- 		local nextSeg=mGraph[mCurrSeg.next].mot
-- 		if true then
-- 			mMotion=MotionDOF(mLoader.dofInfo)
-- 			mMotion:changeLength(prevMotion:length()+nextSeg:length())
-- 			mMotion:range(0, prevMotion:numFrames()-lookAhead):assign( prevMotion:range(0, prevMotion:numFrames()-lookAhead))
-- 			mMotion:range(prevMotion:numFrames()-lookAhead, mMotion:numFrames()):stitch(
-- 			prevMotion:range(prevMotion:numFrames()-lookAhead, prevMotion:numFrames()),
-- 			nextSeg)
-- 		else
-- 			local prevLen=prevMotion:length()+mDelta
-- 			local newLen=prevLen+nextSeg:length()
-- 			local newActualLength=lookAhead+3+nextSeg:length()
-- 			mDelta=newLen-newActualLength
-- 
-- 			mMotion:changeLength(newActualLength)
-- 			mMotion:range(0, prevLen+1-lookAhead-mDelta):assign( 
-- 				prevMotion:range(0, prevLen+1-lookAhead-mDelta))
-- 			mMotion:range(prevLen+1-lookAhead-mDelta, newLen+1-mDelta):stitch(
-- 			prevMotion:range(prevLen+1-lookAhead-mDelta, prevMotion:numFrames()),
-- 			nextSeg)
-- 		end
-- 	end
-- 	mSkin:setPoseDOF(mMotion:row(currFrame))
end

function onCallback(w, userData)
   if w:id()=="button1" then
	   print("button1\n");
   elseif w:id()=="button2" then
	   print("button2\n");
   elseif w:id()=="sliderx"or w:id()=="slidery" then
   end
   print('oncallback')
end

function dtor()
		print('dtor')
end

