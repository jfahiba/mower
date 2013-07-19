package com.boanerges.poc.exception;

public class UnallowedMovementException extends Exception {

	/**
	 * 
	 */
	private static final long serialVersionUID = -63912391384995549L;

	public UnallowedMovementException() {
	}

	public UnallowedMovementException(String message) {
		super(message);
	}

	public UnallowedMovementException(Throwable cause) {
		super(cause);
	}

	public UnallowedMovementException(String message, Throwable cause) {
		super(message, cause);
	}

}
