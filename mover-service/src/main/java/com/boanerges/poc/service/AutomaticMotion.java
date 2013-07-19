package com.boanerges.poc.service;

import java.util.ArrayList;


import com.boanerges.poc.api.AllowedMovement;
import com.boanerges.poc.api.ICoordinateXYC;
import com.boanerges.poc.impl.Position;

public class AutomaticMotion {

	private int mowerNumber;
	private Position initialPosition;
	private ArrayList<AllowedMovement> currentMovements;
	
	public AutomaticMotion(int mowerNumber, Position currentPosition,
			ArrayList<AllowedMovement> currentMovements) {
		super();
		this.mowerNumber = mowerNumber;
		this.initialPosition = currentPosition;
		this.currentMovements = currentMovements;
	}
	
	public int getMowerNumber() {
		return mowerNumber;
	}
	

	public Position finalPosition (ICoordinateXYC upperRight, ICoordinateXYC bottomLeft) {
		Position finalPosition = new Position (initialPosition);
	
		for (AllowedMovement currentMovement : currentMovements) {
			switch (currentMovement) {
			case D:
				finalPosition.turnRight();
				break;
			case G:
				finalPosition.turnLeft();
				break;
			case A: // Send the mower where it is directed
				if (finalPosition.canGoBackward(bottomLeft)) {
					finalPosition.goBackward();
				} else if (finalPosition.canGoForward(upperRight)) {
					finalPosition.goForward();
				} else if (finalPosition.canGoLeft(bottomLeft)){
					finalPosition.goLeft();
				} else if (finalPosition.canGoRight(upperRight)){
					finalPosition.goRight();
				}
				break;
			default:
				break;
				
			}
		}
		return finalPosition;
	}
	
}
