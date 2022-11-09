import com.github.tomakehurst.wiremock.junit.WireMockRule;
import exceptions.BadInputParametersException;
import org.apache.commons.io.FileUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.*;
import platform.types.Dummy;
import platform.types.Incisive;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static com.github.tomakehurst.wiremock.client.WireMock.aResponse;
import static org.junit.Assert.*;

public class TestDownloadConfig {

    @Rule
    public WireMockRule wireMockRule = new WireMockRule(8000);
    public JSONObject downloadConfigAction;
    public static Path configFilePath;
    public static JSONObject configContents;

    @BeforeClass
    public static void beforeClass() throws Exception {
        // delete dummy files
        Files.delete(Paths.get("input/empty.txt"));
        Files.delete(Paths.get("output/empty.txt"));

        // create dummy config file
        configFilePath = Paths.get("src/test/resources/config.json");
        Files.createFile(configFilePath);
        List<String> lines = List.of("{\"test\": \"dummy_json\"}");
        Files.write(configFilePath, lines, StandardCharsets.UTF_8);
        configContents = new JSONObject(lines.get(0));
    }

    @Before
    public void before() throws Exception {
        // create config
        downloadConfigAction = new JSONObject(
                "{" +
                        "\"name\": \"download_config\", " +
                        "\"job_id\": 1" +
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

        FileUtils.cleanDirectory(new File("src/test/resources"));
        Files.createFile(Paths.get("src/test/resources/empty.txt"));
    }

    @Test
    public void downloadConfigSuccess() throws Exception {
        // create mock
        stubFor(get(urlEqualTo("/api/jobs/1/download_ai_engine_config/"))
                .willReturn(aResponse().withBody(Files.readAllBytes(configFilePath))));

        JSONArray actions = new JSONArray();
        actions.put(downloadConfigAction);

        // run domain
        Map<String, Object> incisiveConfig = new HashMap<>();
        incisiveConfig.put("ORCHESTRATOR_SERVICE_HOSTNAME", "localhost:8000");
        Domain domain = new Domain(actions, new Incisive(incisiveConfig));
        domain.run();

        // assure files are ok
        List<String> directoryFiles = listDirectoryFiles("input");
        assertEquals(List.of("config.json"), directoryFiles);
        directoryFiles = listDirectoryFiles("output");
        assertEquals(new ArrayList<>(), directoryFiles);

        // assure config contents are ok
        byte[] actualConfigBytes = Files.readAllBytes(Paths.get("input/config.json"));
        JSONObject actualConfig = new JSONObject(new String(actualConfigBytes, StandardCharsets.UTF_8));
        assertEquals(configContents.toString(), actualConfig.toString());
    }

    @Test
    public void downloadConfigBadFormatted() throws Exception {
        downloadConfigAction = new JSONObject(
                "{" +
                        "\"name\": \"download_config\" " +
                        "}"
        );

        Exception exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(downloadConfigAction);
            Map<String, Object> incisiveConfig = new HashMap<>();
            incisiveConfig.put("ORCHESTRATOR_SERVICE_HOSTNAME", "localhost:8000");
            Domain domain = new Domain(actions, new Incisive(incisiveConfig));
            domain.run();
        });

        String expectedMessage = "Action download config is bad formatted:";
        assertTrue(exception.getMessage().contains(expectedMessage));

        downloadConfigAction = new JSONObject(
                "{" +
                        "\"name\": \"download_config\", " +
                        "\"job_id\": {}" +
                        "}"
        );

        exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(downloadConfigAction);
            Map<String, Object> incisiveConfig = new HashMap<>();
            incisiveConfig.put("ORCHESTRATOR_SERVICE_HOSTNAME", "localhost:8000");
            Domain domain = new Domain(actions, new Incisive(incisiveConfig));
            domain.run();
        });

        expectedMessage = "Action download config is bad formatted:";
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
