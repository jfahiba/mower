package com.boanerges.poc.util;

import java.io.InputStream;
import java.io.OutputStream;

public class CliInfo {
	
	private InputStream in ;
	private OutputStream out;
	private String config;
	
	public CliInfo(InputStream in, OutputStream out, String config) {
		super();
		this.in = in;
		this.out = out;
		this.config = config;
	}

	public InputStream getIn() {
		return in;
	}

	public OutputStream getOut() {
		return out;
	}

	public String getConfig() {
		return config;
	}
	
}
