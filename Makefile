compile:
	g++ -g -c aws_model.cpp -o build/aws_model.o
	g++ -g -c build_simulation.cpp -o build/build_simulation.o
	g++ -g -c csv_parser.cpp -o build/csv_parser.o
	g++ -g build/aws_model.o build/build_simulation.o build/csv_parser.o -o opt -lortools -labsl_log_internal_message

clean:
	rm opt
	rm build/*.o

run:
	./opt

debug:
	gdb opt
