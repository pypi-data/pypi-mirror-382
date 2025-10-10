require("config")
require("module")
require("common")


function ctor()
	this:create("Button", "lturn", "left turn");
	this:create("Button", "rturn", "right turn");
	this:create("Value_Slider", "slidery", "slidery");
	this:widget(0):sliderRange(0,0.5);
	this:widget(0):sliderValue(0.1);
	this:create("Check_Button", "attach camera", "attach camera")
	this:widget(0):buttonShortcut("FL_ALT+c")
	this:create("Check_Button", "draw forward", "draw forward")
	this:findWidget("draw forward"):checkButtonValue(true)
	this:create("Check_Button", "stop", "stop")
	this:updateLayout();

	mCameraInfo=nil
	mLoader=MainLib.VRMLloader ("../Resource/motion/gymnist/gymnist.wrl")

	mMotionDOFcontainer=MotionDOFcontainer(mLoader.dofInfo, '../Resource/motion/gymnist/gymnist.dof')
	mMotionDOF=mMotionDOFcontainer.mot

	-- in meter scale
	for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+0.07)
	end
	mMotionDOF_delta=MotionDOF(mMotionDOF)
	mMotionDOF_delta:convertToDeltaRep();

	-- rendering is done in cm scale
	mSkin= RE.createVRMLskin(mLoader, false);
	mSkin:scale(100,100,100); -- motion data is in meter unit while visualization uses cm unit.
	mSkin:setPoseDOF(mMotionDOF:row(0));

	mGraph={ 
		start={644, 821, next='walk'}, 
		walk={821, 972, next='walk'},
		turn={972,1500, next='turn'}
	}

	for key, seg in pairs(mGraph) do
		seg.mot=mMotionDOF:range(seg[1], seg[2]):copy()
		seg.dmot=mMotionDOF_delta:range(seg[1], seg[2]):copy()
		--print('after')
		--printTable(seg)
	end
	
	mState={
		currSeg=mGraph.start,
		currSegFrame=0,
		currFrame=0,
		pose=mGraph.start.mot:row(0):copy(),
	}
	mTime=0
end

function frameMove(fElapsedTime)
	mTime=mTime+fElapsedTime
	--print(mTime)
	local currFrame=math.round(mTime*120) -- 프레임단위

	local state=mState
	if currFrame>state.currFrame then

		do
			-- test transition, and update state
			local delta=currFrame-state.currFrame
			local currSegFrame=state.currSegFrame+delta
			local currSeg=state.currSeg
			if currSegFrame<currSeg.mot:numFrames() then
				-- use current segment
				state.currSegFrame=currSegFrame
			else
				-- use next segment
				--                  segBound
				--        state.currFrame   currFrame
				--         |
				--                            |
				--                   |
				local segBound=state.currFrame+currSeg.mot:numFrames()-state.currSegFrame
				local remainingFrames=currFrame-segBound
				state.currSeg=mGraph[currSeg.next]
				state.currSegFrame=remainingFrames
			end
			state.currFrame=currFrame
		end
		-- draw current state
		local currPose=state.pose
		local currRootTransform=MotionDOF.rootTransformation(currPose)
		--  dbg.console() 잡아 위 두개 비교해보면, 앞 7차원에 해당.

		local nextPose=state.currSeg.mot:row(state.currSegFrame)
		local nextPoseDeltaRep=state.currSeg.dmot:row(state.currSegFrame)
		-- 위 두개 비교해보면 앞 7차원 빼고는 동일함. delta representation은 앞의 7차원(root 관절 정보)을 이전 프레임에대한 상대적인 위치로 저장함. (회전과 평행이동에 invariant)
		-- 0: dx, 1: dz, 2: dq_y 3: offset_y, 4~6: offset_q (rotation vector)

		mMotionDOF:reconstructOneFrame(currRootTransform:encode2D(), nextPoseDeltaRep, nextPose) -- reconstructOneFrame함수의 정의를 읽어보면 이해갈 것임.
		mSkin:setPoseDOF(nextPose)

		state.pose:assign(nextPose)
		--mSkin:setPoseDOF(state.currSeg.mot:row(state.currSegFrame))
	end
end

currCursorPos=vector3(0,0,0)
function onCallback(w, userData)
   if w:id()=="button1" then
	   print("button1\n");
   elseif w:id()=="button2" then
	   print("button2\n");
   elseif w:id()=="attach camera" then

	   --[[
	   local currFrame=math.round(mTime*120)-- 프레임단위
	   local curPos=mMotion:row(currFrame):toVector3(0)*100
	   mCameraInfo={}
	   mCameraInfo.vpos=RE.viewpoint().vpos-curPos
	   mCameraInfo.vat=RE.viewpoint().vat-curPos
	   ]]
   elseif w:id()=="sliderx"or w:id()=="slidery" then
   elseif w:id()=="lturn" then
   elseif w:id()=="rturn" then
   end
   --print('oncallback')
end

function dtor()
		print('dtor')
end
function dbgDraw(name, pos, color)
	color = color or 'blue'
	dbg._namedDraw('Sphere', pos, name, color, 5)
end

function handleRendererEvent(ev,button,x,y)
	if ev =="PUSH" or 
	ev=="MOVE" or
	ev=="DRAG" or
	ev=="RELEASE" then
		local currFrame=math.round(mTime*120)-- 프레임단위
		--[[
		local curPos=mMotion:row(currFrame):toVector3(0)*100 -- meter to cm
		local curOri=mMotion:row(currFrame):toQuater(3):rotationY()
		local curFrontDir=rotate(vector3(0,0,1), curOri)
		currCursorPos=RE.FltkRenderer():screenToWorldXZPlane(x,y);
		print(currCursorPos)
		dbgDraw("cc",currCursorPos,'blue')

		local changepos=vector3(0,0,0)
		changepos=currCursorPos-curPos

		changepos:normalize()

		dbg.draw('Sphere',changepos*100, 'cc1','red',10)

	
		]]--

	end
		
	return 0
end


function readText()
	local maxText = 5000000;
	out=vectorn()
	local input = util.readFile('testRec.txt')
	structIn = string.lines(input) 
	for i=1,maxText do
		print('i:',i)
		if structIn[i]=='' then
			break;
		else
			out:resize(i);
			out:set(i-1,structIn[i])
		end
	end
	return out
end
