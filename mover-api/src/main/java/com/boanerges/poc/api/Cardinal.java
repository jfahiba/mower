/**
 * 
 */
package com.boanerges.poc.api;

import com.boanerges.poc.exception.CardinalNotFoundException;

/**
 * @author jfahiba
 *
 */
public enum Cardinal {
	
	
	N('N',"North"),
	E('E',"East"),
	W('W',"West"),
	S('S',"South");
	
	private final char cardinalChar;
	private final String cardinalStr;
	
	Cardinal (char cardinalChar, String cardinalStr){
		this.cardinalChar = cardinalChar;
		this.cardinalStr = cardinalStr;
	}
	
	public char getCardinalChar() {
		return cardinalChar;
	}
	
	public String getCardinalStr() {
		return cardinalStr;
	}
	
	public static Cardinal findByKey(char key) throws CardinalNotFoundException{
		Cardinal[] cardinals = Cardinal.values();
        for (Cardinal cardinal : cardinals) {
            if (cardinal.cardinalChar == key) {
                return cardinal;
            }
        }
        throw new CardinalNotFoundException(String.valueOf(key));
    }
	
	/**
	 * 
	 * @return Cardinal at left of current
	 */
	public Cardinal left() {
		switch (this) {
			case N: return W;
			case W: return S;
			case S: return E;
			case E: return N;
		}
		return N;		
	}
	
	/**
	 * 
	 * @return Cardinal at right of current
	 */
	public Cardinal right() {
		switch (this) {
		case N: return E;
		case E: return S;
		case S: return W;
		case W: return N;
		
	}
	return N;
	}
}
