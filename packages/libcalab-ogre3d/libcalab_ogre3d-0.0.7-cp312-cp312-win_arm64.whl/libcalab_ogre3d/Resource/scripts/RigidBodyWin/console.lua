require("config")
require("module")
require("tl")

package.projectPath='../Samples/classification/'
package.path=package.path..";../Samples/classification/lua/?.lua" --;"..package.path


function ctor()
	dbg.console()
	this('exit',0)
end

function dtor()
end

function onCallback(w, userData)
end

function renderOneFrame()
	noFrameMove=true
	RE.renderOneFrame(true)
	noFrameMove=nil
end
function onFrameChanged(currFrame)
end
function frameMove(fElapsedTime)
end
