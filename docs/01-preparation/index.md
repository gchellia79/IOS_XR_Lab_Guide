# 01. Preparation

!!! abstract "Goal"
    Access the dCloud environment, start the lab, and open a device console.

## 1.1 Open the lab session

1. Open the lab-access email supplied for your dCloud session.

    ![Lab-access email](images/image01.png)

2. Alternatively, open [Cisco dCloud](https://dcloud.cisco.com/), sign in with your email address, and select **My Hub**.

    ![dCloud My Hub](images/image02.png)

3. Select **SYD ANZ Datacenter**.

    ![Select the Sydney datacenter](images/image03.png)

4. Select **Sessions**, then **View**.

    ![Open the session](images/image04.png)

5. Review the session view.

    ![dCloud session details](images/image05.png)

## 1.2 Start the lab

1. Select **Ubuntu**.

    ![Ubuntu in the session topology](images/image06.png)

2. Select **Remote Access**, then **VM Console** on the left. Sign in with the supplied lab credentials.
3. Right-click **Chromium Web Browser** and select **Launch (Execute)**.
4. Select **Login::CML2**.

    ![Open Cisco Modeling Labs](images/image07.png)

5. Sign in with the supplied Cisco Modeling Labs credentials, then select **Cisco Modeling Labs**.

    ![Cisco Modeling Labs workspace](images/image08.png)

6. Start the lab.

    ![Start the lab devices](images/image09.png)

7. Wait five minutes for the devices to boot, then select the topology.

    ![Running lab topology](images/image10.png)

| Parameter | Value | Notes |
| --- | --- | --- |
| Datacenter | `SYD ANZ Datacenter` | Select in dCloud |
| Ubuntu credentials | `<username>` / `<password>` | Use the supplied access details |
| Cisco Modeling Labs credentials | `<username>` / `<password>` | Use the supplied access details |
| Boot wait | `5 minutes` | After starting the lab |

## 1.3 Open a device console

1. Right-click a device and select **Console**.

    ![Open a device console](images/image11.png)

2. Sign in using the supplied device credentials and begin the exercises.

    ![Device console](images/image12.png)

!!! tip
    If a router hangs during an exercise, stop and start that device.

## Next step

Continue with [02. Commit configuration](../02-commit-configuration/index.md).