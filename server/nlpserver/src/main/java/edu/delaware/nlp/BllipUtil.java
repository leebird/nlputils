package edu.delaware.nlp;

import java.util.HashMap;

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
        String original = BllipUtil.pennTreeUnEscape.get(word);
        if(original != null) {
            return original;
        }
        return word;
    }
}
