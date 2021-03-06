This plugin creates two actions for downloading images from SecuritySpy.

Example use and setup:

Step 1: Create variables for each of your cameras with the full path to a location to store a snapshot of that camera.

E.g.  outside_camera1_snapshot    /Users/bob/Documents/CameraImages/outside_camera1_snapshot.jpg

Step 2: Copy the IDs for each of the variables

Step 3: Create a "Download URL/SecuritySpy Image" Action or Action Group to download the camera image using this plugin.  Get the camera number for your cameras by using the web interface for SecuritySpy and looking for the "cameraNum" variable in the URL bar when viewing the desired camera.

Step 4: In the action config, enter %%v:XXXXXX%% for the Destination location

Step 5: Try it out.

Step 6: Create pushover notifications with attachments using the same variable.

Step 7: Create triggers for the actions created in previous steps.  For example: Motion detected outside when not home, download outside camera image, send pushover notification.