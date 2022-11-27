
# gather all

./gather-repos.py --dir /tmp/allrepos --user nilsmartel -r solar-lang/research -r solar-lang/solar-ir -r solar-lang/solar-parser
./graph.py --dir /tmp/allrepos
