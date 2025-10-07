KATAPULT_UPSTREAM = Arksine/katapult
KATAPULT_REF = $(shell cat upstream_ref.txt)
PYPROJECT_BUILD = pyproject-build

all: kataflash/upstream/flashtool.py

py: kataflash/upstream/flashtool.py kataflash/upstream/info.py
	pyproject-build
	


kataflash/upstream/flashtool.py kataflash/upstream/info.py: upstream_ref.txt
	curl -L -o kataflash/upstream/flashtool.py "https://github.com/$(KATAPULT_UPSTREAM)/raw/$(KATAPULT_REF)/scripts/flashtool.py"
	echo "KATAPULT_UPSTREAM=\"$(KATAPULT_UPSTREAM)\"\nKATAPULT_REF=\"$(KATAPULT_REF)\"\n" > kataflash/upstream/info.py
	
.PHONY: all
