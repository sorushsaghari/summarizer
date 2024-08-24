-- CreateTable
CREATE TABLE "Channel" (
    "channelID" TEXT NOT NULL PRIMARY KEY,
    "messageID" INTEGER NOT NULL,
    "lastCheck" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateIndex
CREATE UNIQUE INDEX "Channel_channelID_key" ON "Channel"("channelID");
