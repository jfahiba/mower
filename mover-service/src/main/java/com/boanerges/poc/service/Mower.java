/**
 * 
 */
package com.boanerges.poc.service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.apache.commons.cli.Options;

import com.boanerges.poc.api.AllowedMovement;
import com.boanerges.poc.api.ICoordinateXYC;
import com.boanerges.poc.impl.Position;
import com.boanerges.poc.util.CliInfo;
import com.boanerges.poc.util.CommandLineUtil;
import com.boanerges.poc.util.PositionUtil;

/**
 * @author jfahiba
 *
 */
public class Mower {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		Options options = CommandLineUtil.constructOptions();
		CliInfo cliInfo = CommandLineUtil.parseCommandLine(options, args);
		String line = null;
		int mowerNumber = 0;
		BufferedReader reader = new BufferedReader(new InputStreamReader(cliInfo.getIn()));
		ICoordinateXYC upperRight = null;
		ICoordinateXYC bottomLeft = null;
		ArrayList<AutomaticMotion> automaticMotions = new ArrayList<AutomaticMotion>();
		
		try {
			// Parse each line and build automaticMotions list
			while ((line = reader.readLine()) != null) {
				
				if (mowerNumber == 0) {
					upperRight = PositionUtil.upperRight(line);
					bottomLeft = PositionUtil.bottomLeft();
				} else {
					Position currentPosition = PositionUtil.currentPosition (line);
					if  ((line = reader.readLine()) != null) {
						ArrayList<AllowedMovement> currentMovements = PositionUtil.currentMovements (line);
						automaticMotions.add(new AutomaticMotion(mowerNumber, currentPosition, currentMovements));
					} else {
						break;
					}
				}
				mowerNumber++;
			}
			
			Logger.getLogger(Mower.class.getName()).info("All mower motion computed, starting automatic motions.");
			
			// perform all automaticMotions
			final PrintStream printStream = new PrintStream(cliInfo.getOut());
			for (AutomaticMotion automaticMotion : automaticMotions) {
				Position finalPosition = automaticMotion.finalPosition(upperRight, bottomLeft);
				printStream.format("Mower #%d: %d%d%c\n", 
						automaticMotion.getMowerNumber(), 
						finalPosition.getCoordinate_x(),
						finalPosition.getCoordinate_y(),
						finalPosition.getCardinal().getCardinalChar());
			}
			
			
			printStream.close();
			Logger.getLogger(Mower.class.getName()).info("All automatic motions performed.");
			
			
		} catch (IOException e) {
			Logger.getLogger(Mower.class.getName()).log(Level.SEVERE, "Error reading input file.", e);
		} catch (Exception e) {
			Logger.getLogger(Mower.class.getName()).log(Level.SEVERE, "Error parsing line " + line, e);
		}

		
	}

}
