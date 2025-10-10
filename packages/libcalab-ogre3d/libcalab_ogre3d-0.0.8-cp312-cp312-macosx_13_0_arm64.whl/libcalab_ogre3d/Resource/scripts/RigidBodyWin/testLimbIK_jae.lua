require("config")
require("module")
require("common")

function ctor()--생성자
	
	this:create("Button", "button1", "button1");
    
    mLoader=MainLib.VRMLloader ("../Resource/motion/gymnist/gymnist.wrl")
   

	--in meter scale
    for i=0, mMotionDOF:rows()-1 do
		mMotionDOF:matView():set(i, 1, mMotionDOF:matView()(i,1)+0.07)
	end

	--rendering is done in centimeter
    mSkin=RE.createVRMLskin(mLoader, false);
    mSkin:scale(100,100,100);  --motion data are in meter unit while visualization uses cm unit.   



end

function onCallback(w, userData)--callback 함수
   if w:id()=="button1" then
	   print("button 1 pressed");
   end
end

function dtor()--소멸자
end

function frameMove(fElapsedTime)--매 frame마다 불려진다. ctor는 처음에 한번 실행되고, 그다음엔 이게 계속
end
