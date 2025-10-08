require("config")
require("module")
require("common")
require("subRoutines/MatplotLib")

function ctor()
	this:create("Button", "button1", "start");
	this:updateLayout();
	print('ctor')
	MatplotLib.plotFile(
	CT.linspace(0,1,30):column()..
	CT.linspace(0,2,30):column(),'lines.png')
	
end
function frameMove(fElapsedTime)
end

function onCallback(w, userData)
	if w:id()=="button1" then
		plotter=MatplotLib()
		local numSample=30
		local xfn=vectorn(numSample)
		local yfn=vectorn(numSample)
		local yfn2=vectorn(numSample)
		--pendPos(i):x()
		for i=0, numSample-1 do
		xfn:set(i, i)
	--		xfn:set(i, pendPos(i):x())
			yfn:set(i, i)
	--		yfn:set(i, pendPos(i):y())
			yfn2:set(i, i*i/numSample)
		end

		plotter:figure{1, nsubfig={1,1}, subfig_size={3,3}} -- two by one plotting area.
		plotter:add('grid(True)')
		plotter:subplot(0,0)
		plotter:plot(xfn, yfn)
		plotter:plot(yfn2, xfn)
		plotter:plot(xfn, yfn2)
		plotter:xlabel('x')
		plotter:ylabel('t')
		plotter:legends('x(t)', 'y(t)', 'z(t)')
		plotter:savefig('plot.png')
		plotter:close()
	end
end

function dtor()
	print('dtor')
end

