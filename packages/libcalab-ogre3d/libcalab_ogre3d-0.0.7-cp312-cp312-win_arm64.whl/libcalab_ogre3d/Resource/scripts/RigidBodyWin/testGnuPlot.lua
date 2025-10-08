require("config")
require("module")
require("common")
require("subRoutines/MatplotLib")

function ctor()
	print('ctor')
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
		local plotter=gnuPlotQueue(fn, 2, fn)

		local function subplot(xfn, yfn, text)
			local data=matrixn ()
			data:setSize(xfn:size(), 2)
			data:column(0):assign(xfn)
			data:column(1):assign(yfn)
			plotter:plotScattered(data,text)
		end
		subplot(xfn, yfn, 'yfn')
		subplot(xfn+stitched:rows()-xfn:size(), yfn2, 'yfn2')
		subplot(CT.xrange(stitched:rows()), stitched:column(0), 'stitched')

		plotter=nil
		collectgarbage()
		os.execute('gnuplot "'..fn..'.dem"')
	end
	do
		local stitchop=math.linstitch()
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstich')
	end
	do
		local stitchop=math.linstitchOnline()
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstichonline')
	end
	do
		local stitchop=math.linstitch(1)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstich1')
	end
	do
		local stitchop=math.linstitchOnline(1)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstichonline1')
	end
	do
		local stitchop=math.linstitch(0.1)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstich0.1')
	end
	do
		local stitchop=math.linstitchOnline(0.1)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'linstichonline0.1')
	end
	do
		local stitchop=math.c1stitchPreprocess(xfn:size(), yfn:size(), 2.0, true)
		local stitched=matrixn()
		stitchop:calc(stitched, xfn:column(), yfn2:column())
		plot(xfn, yfn2, stitched, 'c1stitch')
	end

end
function frameMove(fElapsedTime)
end

function onCallback(w, userData)
end

function dtor()
	print('dtor')
end

