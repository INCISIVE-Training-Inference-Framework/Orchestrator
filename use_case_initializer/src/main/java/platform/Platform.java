package platform;

import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.http.auth.AuthenticationException;
import org.json.JSONObject;

import java.io.UnsupportedEncodingException;
import java.nio.file.Path;

public interface Platform {

    void downloadConfig(JSONObject config, Path filePath) throws BadInputParametersException, InternalException;

    void downloadModel(JSONObject config, Path directoryPath) throws BadInputParametersException, InternalException;

    void downloadInputData(JSONObject config, Path directoryPath) throws BadInputParametersException, InternalException;

    void downloadInferenceInputData(JSONObject config, Path directoryPath) throws BadInputParametersException, InternalException;

}
