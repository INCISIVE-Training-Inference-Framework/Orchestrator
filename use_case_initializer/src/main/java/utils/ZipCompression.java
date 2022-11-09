package utils;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

public class ZipCompression {

    public static void unZipFile(InputStream inputStream, Path destDirectory) throws IOException {
        File destDir = destDirectory.toFile();
        String parentDirectory = null;
        byte[] buffer = new byte[1024];
        try(ZipInputStream zis = new ZipInputStream(inputStream)) {
            ZipEntry zipEntry = zis.getNextEntry();
            while (zipEntry != null) {
                File newFile = newFile(destDir, zipEntry, parentDirectory);
                if (parentDirectory == null) {
                    parentDirectory = newFile.getName();
                } else {
                    if (zipEntry.isDirectory()) {
                        if (!newFile.isDirectory() && !newFile.mkdirs()) {
                            throw new IOException("Failed to create directory " + newFile);
                        }
                    } else {
                        // fix for windows-created archives
                        File parent = newFile.getParentFile();
                        if (!parent.isDirectory() && !parent.mkdirs()) {
                            throw new IOException("Failed to create directory " + parent);
                        }

                        // write file content
                        FileOutputStream fos = new FileOutputStream(newFile);
                        int len;
                        while ((len = zis.read(buffer)) > 0) {
                            fos.write(buffer, 0, len);
                        }
                        fos.close();
                    }
                }
                zipEntry = zis.getNextEntry();
            }
            zis.closeEntry();
        }
    }

    private static File newFile(File destinationDir, ZipEntry zipEntry, String parentDirectory) throws IOException {
        File destFile;
        if (parentDirectory != null) {
            String destinationPath = destinationDir.getCanonicalPath() + zipEntry.getName().replaceFirst(parentDirectory, "");
            destFile = new File(destinationPath);
        } else {
            destFile = new File(destinationDir, zipEntry.getName());
        }

        String destDirPath = destinationDir.getCanonicalPath();
        String destFilePath = destFile.getCanonicalPath();

        if (!destFilePath.startsWith(destDirPath + File.separator)) {
            throw new IOException("Entry is outside of the target dir: " + zipEntry.getName());
        }

        return destFile;
    }
}
