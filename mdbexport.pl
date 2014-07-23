#!/usr/bin/perl

use strict;

chdir "/media/oldhd/home/stachurski/sql_files";

my $command_tables = "mdb-tables";
my $option_tables = "-1";
my $arg_tables = "decrypted.mdb";
my $command_export = "mdb-export";
my $db_export = "decrypted.mdb";



my @tables = qx($command_tables $option_tables $arg_tables);

for my $table (@tables) {
    chomp $table;
    #print $table, "\n";
}

my @finaltables;

for my $table (@tables) {
    my $newtable = $table;
    $newtable =~ s/acc\_//;
    push @finaltables, $newtable;
}

foreach(0 .. scalar(@tables) ){
	print $tables[$_], "\n";
	print $finaltables[$_], "\n";
}

for (0 .. scalar(@tables)) {
    `$command_export $db_export \"$tables[$_]\" > \"$finaltables[$_].csv\"`;
    system( "sed 's/\"\"//g' -i \"$finaltables[$_].csv\"" ); 
}
