package com.boanerges.poc.util;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.logging.Logger;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.MissingArgumentException;
import org.apache.commons.cli.MissingOptionException;
import org.apache.commons.cli.OptionBuilder;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.PosixParser;


public class CommandLineUtil {

	 
   /**
    * Construct and provide GNU-compatible Options.
    * 
    * @return Options expected from command-line of GNU form.
    */
	@SuppressWarnings("static-access")
	public static Options constructOptions()
	   {
		   Options options = new Options();
		   options.addOption("h", "help", false, "prints the help content");
		   options.addOption(OptionBuilder
		       .withArgName("input file")
		       .hasArg()
		       .isRequired()
		       .withDescription("input file")
		       .withLongOpt("input")
		       .create("i"));
		   options.addOption(OptionBuilder
		       .withArgName("output file")
		       .hasArg()
		       .withDescription("output file")
		       .withLongOpt("output")
		       .create("o"));
		   options.addOption(OptionBuilder
		       .withArgName("config file")
		       .hasArg()
		       .withDescription("configuration file")
		       .withLongOpt("config")
		       .create("c"));
	      return options;
	   }
	
	public static CliInfo parseCommandLine(Options options, String[] args) {
		 try{
	
		      CommandLineParser parser = new GnuParser();
		      CommandLine cmd = parser.parse(options, args);

		      InputStream in = new FileInputStream(cmd.getOptionValue("i"));
		      // Write answer to console by default
		      OutputStream out = System.out;
		      if(cmd.hasOption("o"))
		         out = new FileOutputStream(cmd.getOptionValue("o"));
		      String config = cmd.getOptionValue("c", "app.cfg"); 
		      return new CliInfo(in, out, config);
		   }
		   catch(MissingOptionException e){
		      // Check if -h option is present
		      boolean help = false;
		      try{
		         Options helpOptions = new Options();
		         helpOptions.addOption("h", "help", false, "prints the help content");
		         CommandLineParser parser = new PosixParser();
		         CommandLine line = parser.parse(helpOptions, args);
		         if(line.hasOption("h")) help = true;
		      }
		      catch(Exception ex){ }
		      if(!help) Logger.getLogger("CLI").severe(e.getMessage());
		      HelpFormatter formatter = new HelpFormatter();
		      formatter.printHelp( "Mover" , options );
		      
		   } catch(MissingArgumentException e){
			   Logger.getLogger("CLI").severe(e.getMessage());
		      HelpFormatter formatter = new HelpFormatter();
		      formatter.printHelp( "Mover" , options );
		    
		   } catch(ParseException e){
			   Logger.getLogger("CLI").severe("Error while parsing the command line: "+e.getMessage());
		   } catch(Exception e){
		       e.printStackTrace();  
		    }
		 System.exit(1);
		 return null;
	}

}
