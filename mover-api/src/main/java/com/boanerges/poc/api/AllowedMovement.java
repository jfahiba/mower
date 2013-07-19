/**
 * 
 */
package com.boanerges.poc.api;

import com.boanerges.poc.exception.UnallowedMovementException;

/**
 * @author jfahiba
 *
 */
public enum AllowedMovement {
	
	D('D',"Right"),
	G('G',"Left"),
	A('A',"Forward");
	
	private final char movementChar;
	private final String movementStr;
	
	AllowedMovement (char movementChar, String movementStr){
		this.movementChar = movementChar;
		this.movementStr = movementStr;
	}
	public char getMovementChar() {
		return movementChar;
	}
	public String getMovementStr() {
		return movementStr;
	}

	public static AllowedMovement findByKey(char key) throws UnallowedMovementException{
		AllowedMovement[] movements = AllowedMovement.values();
        for (AllowedMovement movement : movements) {
            if (movement.movementChar == key) {
                return movement;
            }
        }
        throw new UnallowedMovementException(String.valueOf(key));
    }
	
}
