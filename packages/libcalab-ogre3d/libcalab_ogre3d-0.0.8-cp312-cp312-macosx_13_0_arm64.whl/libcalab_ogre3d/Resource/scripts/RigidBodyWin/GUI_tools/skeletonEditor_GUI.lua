require("config")
require("common")
require("module")
require("RigidBodyWin/retargetting/skeletonEditor")

config=nil

ctor_original=ctor
onCallback_original=onCallback



function ctor()
	this:create("Button", "start", "start");
	this:create("Button", "Start (script)", "start (script)");
	this:updateLayout()
end


-- see also skeletonEditor.lua
function onCallback(w, userData)
	if w:id()=="start" then
		local path='../Resource/motion'
		local chosenFile=Fltk.chooseFile("Choose a wrl file to edit", path, "*.wrl", false)

		if chosenFile ~='' then
			local chosenFile2=Fltk.chooseFile("Choose a dof file to view", path, "*.dof", false)
			if chosenFile2~=''  then
				config={
					skel=chosenFile,
					motion=chosenFile2,
					skinScale=100}
				ctor_original()
			end
		end
		if not config then
			util.msgBox("??")
		end
	elseif w:id()=="Start (script)" then
		local filename=Fltk.chooseFile('choose a script file', '../Resource/scripts/modifyModel/' ,'*.lua', false)
		if filename~='' then
			function Start(a,b,c,d)
				config={ skel=a, motion=b, skinScale=d}
			end
			dofile(filename)
			ctor_original()
		end
	else
		onCallback_original(w, userData)
	end
end
