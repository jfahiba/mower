/**
 * 
 */
package com.boanerges.poc.impl;

import com.boanerges.poc.api.Cardinal;
import com.boanerges.poc.api.ICoordinateXYC;
import com.boanerges.poc.api.IMovableXYC;

/**
 * @author jfahiba
 *
 */
public class Position implements IMovableXYC, ICoordinateXYC{
	
	private int coordinate_x;
	private int coordinate_y;
	private Cardinal cardinal;
	
	///////////////////////////////////////////////////////
	// Constructors
	///////////////////////////////////////////////////////
	
	public Position(int coordinate_x, int coordinate_y) {
		this(coordinate_x, coordinate_y, Cardinal.N);
	}
	
	public Position(int coordinate_x, int coordinate_y, Cardinal cardinal) {
		super();
		this.coordinate_x = coordinate_x;
		this.coordinate_y = coordinate_y;
		this.cardinal = cardinal;
	}
	
	///////////////////////////////////////////////////////
	// ICoordinateXYC implementation
	///////////////////////////////////////////////////////
	
	public Position(Position position) {
		this(position.coordinate_x, position.coordinate_y, position.cardinal);
	}

	public int getCoordinate_x() {
		return coordinate_x;
	}

	public int getCoordinate_y() {
		return coordinate_y;
	}

	public Cardinal getCardinal() {
		return cardinal;
	}

	///////////////////////////////////////////////////////
	// IMovableXYC implementation
	///////////////////////////////////////////////////////
	
	public void turnLeft() {
		cardinal = cardinal.left();
	}

	public void turnRight() {
		cardinal = cardinal.right();
	}
	
	public void goLeft() {
		coordinate_x--;
	}

	public void goRight() {
		coordinate_x++;
	}

	public void goForward() {
		coordinate_y++;
	}
	
	public void goBackward() {
		coordinate_y--;
	}
	
	public boolean canGoRight(ICoordinateXYC upperRight) {
		return cardinal == Cardinal.E &&  coordinate_x < upperRight.getCoordinate_x();
	}

	public boolean canGoForward(ICoordinateXYC upperRight) {
		return cardinal == Cardinal.N  && coordinate_y < upperRight.getCoordinate_y();
	}
	
	public boolean canGoLeft(ICoordinateXYC bottomLeft) {
		return cardinal == Cardinal.W  && coordinate_x > bottomLeft.getCoordinate_x();
	}

	public boolean canGoBackward(ICoordinateXYC bottomLeft) {
		return cardinal == Cardinal.S  && coordinate_y > bottomLeft.getCoordinate_y();
	}

}
