require("config")
require("module")
require("common")

function ctor()
--	this:create("Button", "button1", "button1");
--	this:create("Value_Slider", "slidery", "slidery");
--	this:widget(0):sliderRange(0,0.5);
--	this:widget(0):sliderValue(0.1);
	this:updateLayout();

	--mLoader=MainLib.VRMLloader ("../Resource/mesh/left_leg.wrl") --안됨
	--mLoader=MainLib.VRMLloader ("../Resource/mesh/sample.wrl") --안됨
	--mLoader=MainLib.VRMLloader ("../Resource/motion/gymnist/gymnist.wrl")
	--mLoader=MainLib.VRMLloader ("../Samples/classification/Resource/cart_pole_ball.wrl")
    --mLoader=MainLib.VRMLloader ("../Resource/mesh/simple.wrl")
	mLoader=MainLib.VRMLloader ("../Resource/mesh/hand.wrl")


	-- rendering is done in cm scale. wrl file (the skeleton) is usually in meter scale.
	mSkin= RE.createVRMLskin(mLoader, true);
	mSkin:scale(100,100,100); -- motion data is in meter unit while visualization uses cm unit.
	mSkin:setThickness(0.1);

	print('ctor')
end
function frameMove()
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

