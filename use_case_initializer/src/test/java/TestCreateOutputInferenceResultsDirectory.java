import exceptions.BadInputParametersException;
import org.apache.commons.io.FileUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.*;
import platform.types.Dummy;

import java.io.File;
import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.*;

public class TestCreateOutputInferenceResultsDirectory {

    public JSONObject createOutputInferenceResultsDirectoryAction;

    @BeforeClass
    public static void beforeClass() throws Exception {
        // delete dummy files
        Files.delete(Paths.get("input/empty.txt"));
        Files.delete(Paths.get("output/empty.txt"));
    }

    @Before
    public void before() throws Exception {
        // create config
        createOutputInferenceResultsDirectoryAction = new JSONObject(
                "{" +
                        "\"name\":\"create_output_inference_results_directory\"" +
                        "}"
        );
    }

    @After
    public void after() throws Exception {
        // clean test environment
        FileUtils.cleanDirectory(new File("input"));
        FileUtils.cleanDirectory(new File("output"));
    }

    @AfterClass
    public static void afterClass() throws Exception {
        // create dummy files
        Files.createFile(Paths.get("input/empty.txt"));
        Files.createFile(Paths.get("output/empty.txt"));
    }

    @Test
    public void createOutputInferenceResultsDirectorySuccess() throws Exception {
        JSONArray actions = new JSONArray();
        actions.put(createOutputInferenceResultsDirectoryAction);

        // run domain
        Domain domain = new Domain(actions, new Dummy());
        domain.run();

        // assure files are ok
        List<String> directoryFiles = listDirectoryFiles("input");
        assertEquals(new ArrayList<>(), directoryFiles);
        directoryFiles = listDirectoryFiles("output");
        assertEquals(List.of("inference_results"), directoryFiles);
    }

    @Test
    public void createOutputInferenceResultsDirectoryBadFormatted() throws Exception {
        createOutputInferenceResultsDirectoryAction = new JSONObject(
                "{" +
                        "\"nothing\":\"create_output_inference_results_directory\"" +
                        "}"
        );

        Exception exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(createOutputInferenceResultsDirectoryAction);
            Domain domain = new Domain(actions, new Dummy());
            domain.run();
        });

        String expectedMessage = "At least one of the actions is bad formatted:";
        assertTrue(exception.getMessage().contains(expectedMessage));

        createOutputInferenceResultsDirectoryAction = new JSONObject(
                "{}"
        );

        exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(createOutputInferenceResultsDirectoryAction);
            Domain domain = new Domain(actions, new Dummy());
            domain.run();
        });

        expectedMessage = "At least one of the actions is bad formatted:";
        assertTrue(exception.getMessage().contains(expectedMessage));

        createOutputInferenceResultsDirectoryAction = new JSONObject(
                "{" +
                        "\"nothing\": 1" +
                        "}"
        );

        exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(createOutputInferenceResultsDirectoryAction);
            Domain domain = new Domain(actions, new Dummy());
            domain.run();
        });

        expectedMessage = "At least one of the actions is bad formatted:";
        assertTrue(exception.getMessage().contains(expectedMessage));

        expectedMessage = "At least one of the actions is bad formatted:";
        assertTrue(exception.getMessage().contains(expectedMessage));

        exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put("1");
            Domain domain = new Domain(actions, new Dummy());
            domain.run();
        });

        expectedMessage = "At least one of the actions is bad formatted:";
        assertTrue(exception.getMessage().contains(expectedMessage));
    }

    private static List<String> listDirectoryFiles(String dir) throws IOException {
        List<String> directoryFiles = new ArrayList<>();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get(dir))) {
            for (Path path : stream) {
                if (!Files.isDirectory(path)) {
                    directoryFiles.add(path.getFileName().toString());
                } else {
                    directoryFiles.add(path.getFileName().toString());
                    directoryFiles.addAll(listDirectoryFiles(path.toString()));
                }
            }
        }
        return directoryFiles;
    }

}
