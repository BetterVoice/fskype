fskype
======

A python module to launch Skype clients programmtically for the FreeSWITCH SkypOpen Module.

Below is an example configuration that will be passed into the module. Keep in mind that the module will try to use the X11-display assigned in the configuration.

```xml
<configuration name="skypopen.conf" description="Skype open configuration">
  <global_settings> 
    <param name="dialplan" value="XML"/>
    <param name="context" value="default"/>
    <param name="report_incoming_chatmessages" value="false"/>
    <param name="silent_mode" value="false"/>
    <param name="write_silence_when_idle" value="false"/>
    <param name="setsockopt" value="true"/>     
  </global_settings>
  <!-- one entry follows per each skypopen interface -->
  <per_interface_settings>
    <interface id="1" name="better.voice">
      <param name="X11-display" value=":101"/>
      <param name="destination" value="5000"/>
      <param name="skype_user" value="user1"/>
      <param name="skype_password" value="password1">
    </interface>
    <interface id="2" name="better.voice1">
      <param name="X11-display" value=":201"/>
      <param name="destination" value="5001"/>
      <param name="skype_user" value="user2"/>
      <param name="skype_password" value="password2">
    </interface>
  </per_interface_settings>
</configuration>
```

Example:
```python
skypopen = SkypOpenModule()
skypopen.configure(xml)
```
After configure is called FreeSWITCH has to reload the skype clients by calling `sk reload`.

To clean up:
```python
skypopen.shutdown()
```