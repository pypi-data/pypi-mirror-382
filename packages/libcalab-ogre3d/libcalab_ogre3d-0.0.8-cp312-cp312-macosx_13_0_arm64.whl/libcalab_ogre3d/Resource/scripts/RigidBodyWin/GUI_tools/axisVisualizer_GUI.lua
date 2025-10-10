require("config")
require("common")
require("module")
require("RigidBodyWin/retargetting/axisVisualizer")

config=nil
ctor_original=ctor
onCallback_original=onCallback
mMot={}

function ctor()
	this:create("Button", "start (lua)", "start (lua)");
	this:widget(0):buttonShortcut("FL_ALT+s");
	this:create("Button", "start (eeconfig)", "start (eeconfig)");
	this:create("Button", "start (asf/amc)", "start (asf/amc)");
	this:create("Button", "start (wrl/dof)", "start (wrl/dof)");
	this:updateLayout()
end


function onCallback(w, userData)
	local motion_path="../Resource/motion/"
	if w:id()=="start (lua)" then
		local path='../Resource/scripts/modifyModel'
		local chosenFile=Fltk.chooseFile("Choose ", path, "*.lua", false)
		if chosenFile~='' then
			function Start(skel1, mot, initialHeight, skinScale)
				config={{skel=skel1, motion=mot, skinScale=skinScale}}
			end
			dofile(chosenFile)
			ctor_original()
		end
	elseif w:id()=="start (eeconfig)" then
		local path='../Resource/motion'
		local chosenFile=Fltk.chooseFile("Choose a EEconfig file", path, "*.EEconfig.lua", false)

		if chosenFile then
			local fno,msg=loadfile(chosenFile)
			if not fno then print(msg) return end
			config={fno()}
			ctor_original()
		else
			return 
		end
	elseif w:id()=="start (asf/amc)" then
	   local chosenFile=Fltk.chooseFile("Choose a ASF file to view", motion_path, "*.asf", false)
	   if chosenFile~="" then
		   local chosenFile2=Fltk.chooseFile("Choose a AMC file to view", motion_path, "*.amc", false)
		   if chosenFile2~="" then 
			   config={{
				   skel=chosenFile,
				   motion=chosenFile2,
				   skinScale=1,
			   }}
			   ctor_original()
		   end
	   end
	elseif w:id()=="start (wrl/dof)" then
	   local chosenFile=Fltk.chooseFile("Choose a wrl file to view", motion_path, "*.wrl", false)
	   if chosenFile~="" then
		   local chosenFile2=Fltk.chooseFile("Choose a dof file to view", motion_path, "*.dof", false)
		   if chosenFile2~="" then 
			   config={{
				   skel=chosenFile,
				   motion=chosenFile2,
				   skinScale=100,
			   }}
			   ctor_original()
		   end
	   end
	else
		onCallback_original(w, userData)
	end
end
