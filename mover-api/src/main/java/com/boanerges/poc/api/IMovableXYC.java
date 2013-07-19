/**
 * 
 */
package com.boanerges.poc.api;

/**
 * @author jfahiba
 *
 */
public interface IMovableXYC {
	
	void turnLeft();
	void turnRight();
	
	void goLeft();
	void goRight();
	void goForward();
	void goBackward();
	
	boolean canGoRight(ICoordinateXYC upperRight);
	boolean canGoLeft(ICoordinateXYC bottomLeft);
	boolean canGoForward(ICoordinateXYC upperRight);
	boolean canGoBackward(ICoordinateXYC bottomLeft);
	
}
