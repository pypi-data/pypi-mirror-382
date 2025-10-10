require("config")
require("common")
require("module")
require("RigidBodyWin/retargetting/rigidRiggingAndRetargettingTool")

A=nil
B=nil

function ctor()


	local st_backup=RE.ogreSceneManager():getShadowTechnique()
	RE.ogreSceneManager():setShadowTechnique(0) -- turn off shadow for faster rendering
	
	this:create("Button", "start", "start",0);
	this:create("Button", "start using script", "start using script",0);
	this:widget(0):buttonShortcut("FL_CTRL+s")
	this:create("Button", "start using retargetConfig", "start using retargetConfig",0);
	this:widget(0):buttonShortcut("FL_ALT+s")

	createUI()

	--dbg.startTrace()
	mEventReceiver=EVR()


	camInfo={}

end
