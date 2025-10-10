require("config")
require("module")
require("common")
require("subRoutines/MatplotLib")

function ctor()
	print('ctor')
	plotter=MatplotLib()
	local numSample=30
	local xfn=vectorn(numSample)
	local yfn=vectorn(numSample)
	local yfn2=vectorn(numSample)
	for i=0, numSample-1 do
		xfn:set(i, i)
		--		xfn:set(i, pendPos(i):x())
		yfn:set(i, i)
		--		yfn:set(i, pendPos(i):y())
		yfn2:set(i, i*i/numSample)
	end

	function plot(xfn, yfn2, stitched, fn)
		plotter:figure{1, nsubfig={1,1}, subfig_size={3,3}} -- two by one plotting area.
		plotter:add('grid(True)')
		plotter:subplot(0,0)
		plotter:plot(xfn, yfn)
		--plotter:plot(yfn2, xfn)
		plotter:plot(xfn+stitched:rows()-xfn:size(), yfn2)
		plotter:plot(CT.xrange(stitched:rows()), stitched:column(0))
		plotter:xlabel('x')
		plotter:ylabel('t')
		--plotter:legends('x(t)', 'z(t)')
		plotter:savefig(fn)
		plotter:close()
	end
	do
		local stitchop=math.linstitch()
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstich.png')
	end
	do
		local stitchop=math.linstitchOnline()
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstichonline.png')
	end
	do
		local stitchop=math.linstitchForward()
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstichForward.png')
	end
	do
		local stitchop=math.linstitch(1)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstich1.png')
	end
	do
		local stitchop=math.linstitchOnline(1)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstichonline1.png')
	end
	do
		local stitchop=math.linstitch(0.1)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstich0.1.png')
	end
	do
		local stitchop=math.linstitchOnline(0.1)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstichonline0.1.png')
	end
	do
		local stitchop=math.c1stitchPreprocess(xfn:size(), yfn:size(), 2.0, true)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'c1stitch.png')
	end
	do
		-- new : quintic stitch
		local x0=yfn(0)-xfn(xfn:size()-1) 
		local v0=yfn(1)-yfn(0) - (xfn(xfn:size()-1)  - xfn(xfn:size()-2))
		--local a0=yfn(2)-2*yfn(1)+yfn(0) - (xfn(-1)-2*xfn(-2)+xfn(-3))
		local a0=0 -- works equally well.


		-- displacement map
		local out=vectorn(yfn:size())
		out:quintic(x0, v0, 0, 0,0,0, out:size())
		
		local stitched=matrixn(xfn:size()+yfn:size()-1, 1)

		stitched:column(0):range(0,xfn:size()):assign(xfn)
		stitched:column(0):slice(xfn:size()-1,0):assign(yfn)
		stitched:column(0):slice(xfn:size()-1,0):rsub(out)
		plot(xfn, yfn2, stitched, 'qstitch.png')
	end

end
function frameMove(fElapsedTime)
end

function onCallback(w, userData)
end

function dtor()
	print('dtor')
end

