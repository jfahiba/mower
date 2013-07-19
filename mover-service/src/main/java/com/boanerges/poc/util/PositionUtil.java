package com.boanerges.poc.util;


import java.util.ArrayList;

import com.boanerges.poc.api.AllowedMovement;
import com.boanerges.poc.api.Cardinal;
import com.boanerges.poc.api.ICoordinateXYC;
import com.boanerges.poc.exception.CardinalNotFoundException;
import com.boanerges.poc.exception.InvalidCoordinatesException;
import com.boanerges.poc.exception.UnallowedMovementException;
import com.boanerges.poc.impl.Position;

public class PositionUtil {
	
	/**
	 * 
	 * @return (0,0) by default
	 */
	static public ICoordinateXYC bottomLeft() {
		return new Position(0, 0);
	}
	
	/**
	 * 
	 * @param line
	 * @return upperRight coordinates
	 * @throws InvalidCoordinatesException when there is line format errors
	 */
	static public ICoordinateXYC upperRight(String line) throws InvalidCoordinatesException {
		if (line.length() != 2) throw new InvalidCoordinatesException(line);
		
		String upper_x = String.valueOf(line.charAt(0));
		String upper_y = String.valueOf(line.charAt(1));
		try {
			return new Position(Integer.parseInt(upper_x), Integer.parseInt(upper_y));
		} catch (NumberFormatException e) {
			throw new InvalidCoordinatesException(line, e);
		}
	}

	/**
	 * 
	 * @param line
	 * @return current position
	 * @throws CardinalNotFoundException
	 * @throws InvalidCoordinatesException
	 */
	public static Position currentPosition(String line) 
			throws CardinalNotFoundException, InvalidCoordinatesException {
		
		if (line.length() != 3) throw new InvalidCoordinatesException(line);
		
		String upper_x = String.valueOf(line.charAt(0));
		String upper_y = String.valueOf(line.charAt(1));
		Cardinal cardinal =  Cardinal.findByKey(line.charAt(2));
		try {
			return new Position(Integer.parseInt(upper_x), Integer.parseInt(upper_y), cardinal);
		} catch (NumberFormatException e) {
			throw new InvalidCoordinatesException(line, e);
		}
	}

	/**
	 * 
	 * @param line
	 * @return
	 * @throws UnallowedMovementException if a programmed movement in unknown
	 */
	public static ArrayList<AllowedMovement> currentMovements(String line) throws UnallowedMovementException {
		ArrayList<AllowedMovement> currentMovements = new ArrayList<AllowedMovement>(line.length());
		
		for (int i = 0; i < line.length(); i++) {
			currentMovements.add(AllowedMovement.findByKey(line.charAt(i)));
		}
		return currentMovements;
	}
}
