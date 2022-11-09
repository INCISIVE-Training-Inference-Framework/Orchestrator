package platform.types;

import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;
import platform.Platform;

import java.nio.file.Path;

public class Dummy implements Platform {

    private static final Logger logger = LogManager.getLogger(Dummy.class);

    @Override
    public void downloadConfig(JSONObject config, Path filePath) throws BadInputParametersException, InternalException {
        logger.debug("downloadConfig method called");
    }

    @Override
    public void downloadModel(JSONObject config, Path directoryPath) throws BadInputParametersException, InternalException {
        logger.debug("downloadModel method called");
    }

    @Override
    public void downloadInputData(JSONObject config, Path directoryPath) throws BadInputParametersException, InternalException {
        logger.debug("downloadInputData method called");
    }

    @Override
    public void downloadInferenceInputData(JSONObject config, Path directoryPath) throws BadInputParametersException, InternalException {
        logger.debug("downloadInferenceInputData method called");
    }
}
