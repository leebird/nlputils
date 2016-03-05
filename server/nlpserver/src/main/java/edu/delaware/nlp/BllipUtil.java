package edu.delaware.nlp;

import java.util.HashMap;
import java.util.Map;

public class BllipUtil {
    private static final HashMap<String, String> pennTreeUnEscape;
    static {
        pennTreeUnEscape = new HashMap<String, String>();
        pennTreeUnEscape.put("-LRB-","(");
        pennTreeUnEscape.put("-RRB-",")");
        pennTreeUnEscape.put("-LCB-", "{");
        pennTreeUnEscape.put("-RCB-", "}");
        pennTreeUnEscape.put("-LSB-", "[");
        pennTreeUnEscape.put("-RSB-", "]");
    }

    public static String unescape(String word) {
	for(Map.Entry<String, String> entry : BllipUtil.pennTreeUnEscape.entrySet()) {
	    String pennEscaped = entry.getKey();
	    String original = entry.getValue();	
	    word = word.replace(pennEscaped, original);
	}

        return word;
    }
}
