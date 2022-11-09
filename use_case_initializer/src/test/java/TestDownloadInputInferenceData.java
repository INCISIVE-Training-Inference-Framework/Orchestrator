import com.github.tomakehurst.wiremock.junit.WireMockRule;
import exceptions.BadInputParametersException;
import exceptions.InternalException;
import org.apache.commons.io.FileUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.*;
import platform.types.Incisive;

import java.io.*;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static com.github.tomakehurst.wiremock.client.WireMock.*;
import static org.junit.Assert.*;

public class TestDownloadInputInferenceData {

    @Rule
    public WireMockRule wireMockRule = new WireMockRule(8000);
    public JSONObject downloadDataAction;
    public static ByteArrayOutputStream byteArrayOutputStream;

    @BeforeClass
    public static void beforeClass() throws Exception {
        // delete dummy files
        Files.delete(Paths.get("input/empty.txt"));
        Files.delete(Paths.get("output/empty.txt"));

        // create dummy zip compressed file
        Path image1FilePath = Paths.get("src/test/resources/inference_data/image1.png");
        Path image2FilePath = Paths.get("src/test/resources/inference_data/image2.png");
        Files.createDirectory(Paths.get("src/test/resources/inference_data"));
        Files.createFile(image1FilePath);
        Files.createFile(image2FilePath);
        byteArrayOutputStream = new ByteArrayOutputStream();
        zipFile(new File("src/test/resources/inference_data"), "inference_data", byteArrayOutputStream);
    }

    @Before
    public void before() throws Exception {
        // create config
        downloadDataAction = new JSONObject(
                "{" +
                        "\"name\": \"download_data\", " +
                        "\"method\": {" +
                                        "\"name\": \"inference_input_data\"," +
                                        "\"job_id\": 1" +
                                     "}" +
                        "}"
        );
    }

    @After
    public void after() throws Exception {
        // clean test environment
        FileUtils.cleanDirectory(new File("src/test/resources"));
        FileUtils.cleanDirectory(new File("input"));
        FileUtils.cleanDirectory(new File("output"));
    }

    @AfterClass
    public static void afterClass() throws Exception {
        // create dummy files
        Files.createFile(Paths.get("input/empty.txt"));
        Files.createFile(Paths.get("output/empty.txt"));
        Files.createFile(Paths.get("src/test/resources/empty.txt"));

        // close byte array
        byteArrayOutputStream.close();
    }

    @Test
    public void downloadInputInferenceDataSuccess() throws Exception {
        // create mock
        stubFor(get(urlEqualTo("/api/jobs/1/download_input_data_files/"))
                .willReturn(aResponse().withBody(byteArrayOutputStream.toByteArray())));

        // run domain
        JSONArray actions = new JSONArray();
        actions.put(downloadDataAction);
        Map<String, Object> incisiveConfig = new HashMap<>();
        incisiveConfig.put("ORCHESTRATOR_SERVICE_HOSTNAME", "localhost:8000");
        Domain domain = new Domain(actions, new Incisive(incisiveConfig));
        domain.run();

        // assure files are ok
        List<String> directoryFiles = listDirectoryFiles("input");
        assertEquals(Arrays.asList("data", "image1.png", "image2.png"), directoryFiles);
        directoryFiles = listDirectoryFiles("output");
        assertEquals(new ArrayList<>(), directoryFiles);
    }

    @Test
    public void downloadInputInferenceDataFailed() throws Exception {
        // create mock
        stubFor(get(urlEqualTo("/api/jobs/1/download_input_data_files/"))
                .willReturn(aResponse().withStatus(400).withBody("")));

        Exception exception = assertThrows(InternalException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(downloadDataAction);
            Map<String, Object> incisiveConfig = new HashMap<>();
            incisiveConfig.put("ORCHESTRATOR_SERVICE_HOSTNAME", "localhost:8000");
            Domain domain = new Domain(actions, new Incisive(incisiveConfig));
            domain.run();
        });

        String expectedMessage = "Error while downloading input inference data files from MaaS";
        assertTrue(exception.getMessage().contains(expectedMessage));
    }

    @Test
    public void downloadInputInferenceDataBadFormatted() throws Exception {
        downloadDataAction = new JSONObject(
                "{" +
                        "\"name\": \"download_data\", " +
                        "}"
        );
        Exception exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(downloadDataAction);
            Map<String, Object> incisiveConfig = new HashMap<>();
            incisiveConfig.put("ORCHESTRATOR_SERVICE_HOSTNAME", "localhost:8000");
            Domain domain = new Domain(actions, new Incisive(incisiveConfig));
            domain.run();
        });

        String expectedMessage = "Action download data bad formatted";
        assertTrue(exception.getMessage().contains(expectedMessage));

        downloadDataAction = new JSONObject(
                "{" +
                        "\"name\": \"download_data\", " +
                        "\"method\": {" +
                        "\"name\": \"meh\"," +
                        "\"job_id\": 1" +
                        "}" +
                        "}"
        );
        exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(downloadDataAction);
            Map<String, Object> incisiveConfig = new HashMap<>();
            incisiveConfig.put("ORCHESTRATOR_SERVICE_HOSTNAME", "localhost:8000");
            Domain domain = new Domain(actions, new Incisive(incisiveConfig));
            domain.run();
        });

        expectedMessage = "Method for action download data not recognized";
        assertTrue(exception.getMessage().contains(expectedMessage));

        downloadDataAction = new JSONObject(
                "{" +
                        "\"name\": \"download_data\", " +
                        "\"method\": {" +
                        "\"name\": \"inference_input_data\"," +
                        "}" +
                        "}"
        );
        exception = assertThrows(BadInputParametersException.class, () -> {
            JSONArray actions = new JSONArray();
            actions.put(downloadDataAction);
            Map<String, Object> incisiveConfig = new HashMap<>();
            incisiveConfig.put("ORCHESTRATOR_SERVICE_HOSTNAME", "localhost:8000");
            Domain domain = new Domain(actions, new Incisive(incisiveConfig));
            domain.run();
        });

        expectedMessage = "Action download input inference data is bad formatted";
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

    public static void zipFile(File fileToZip, String fileName, OutputStream outputStream) throws IOException {
        try(ZipOutputStream zipOut = new ZipOutputStream(outputStream)) {
            zipFileRecursive(fileToZip, fileName, zipOut);
        }
    }
    private static void zipFileRecursive(File fileToZip, String fileName, ZipOutputStream zipOut) throws IOException {
        if (fileToZip.isHidden()) {
            return;
        }
        if (fileToZip.isDirectory()) {
            if (fileName.endsWith("/")) {
                zipOut.putNextEntry(new ZipEntry(fileName));
                zipOut.closeEntry();
            } else {
                zipOut.putNextEntry(new ZipEntry(fileName + "/"));
                zipOut.closeEntry();
            }
            final File[] children = fileToZip.listFiles();
            for (final File childFile : children) {
                zipFileRecursive(childFile, fileName + "/" + childFile.getName(), zipOut);
            }
            return;
        }
        try(FileInputStream fis = new FileInputStream(fileToZip)) {
            ZipEntry zipEntry = new ZipEntry(fileName);
            zipOut.putNextEntry(zipEntry);
            byte[] bytes = new byte[1024];
            int length;
            while ((length = fis.read(bytes)) >= 0) {
                zipOut.write(bytes, 0, length);
            }
        }
    }

}
