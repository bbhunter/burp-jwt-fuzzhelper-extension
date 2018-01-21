from burp import IBurpExtender
from burp import IIntruderPayloadProcessor
from burp import ITab
from burp import IBurpExtenderCallbacks


from java.awt import Component;
from java.io import PrintWriter;
from java.util import ArrayList;
from java.util import List;

from java.awt import BorderLayout;
from java.awt import GridBagLayout;
from java.awt import GridBagConstraints;
from java.awt import Insets;
from java.awt import Font;
from java.awt import Dimension;
from javax.swing import JScrollPane;
from javax.swing import ImageIcon;
from javax.swing import JFrame;
from javax.swing import JLabel;
from javax.swing import JButton;
from javax.swing import JPanel;
from javax.swing import JComboBox;
from javax.swing import JSplitPane;
from javax.swing import JTabbedPane;
from javax.swing import JTable;
from javax.swing import SwingUtilities;
from javax.swing import JTextField;
from javax.swing import JTextArea;
from javax.swing.table import AbstractTableModel;
import jwt
import re
import json

# Insets: https://docs.oracle.com/javase/7/docs/api/java/awt/Insets.html


class BurpExtender(IBurpExtender, IBurpExtenderCallbacks, IIntruderPayloadProcessor, ITab):
    def registerExtenderCallbacks( self, callbacks):
        self._helpers = callbacks.getHelpers()
        callbacks.setExtensionName("JWT Fuzzer")
        callbacks.registerIntruderPayloadProcessor(self)
        
        self._fuzzoptions = { 
                                "target" : "Header", 
                                "selector" : None, 
                                "signature" : False,
                                "algorithm" : "HS256",
                                "key" : ""
                            }

        # Configuration panel Layout
        self._configurationPanel = JPanel()
        gridBagLayout = GridBagLayout()
        gridBagLayout.columnWidths = [ 0, 0 ]
        gridBagLayout.rowHeights = [ 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        gridBagLayout.columnWeights = [ 0.0, 0.0 ]
        gridBagLayout.rowWeights = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0 ]
        self._configurationPanel.setLayout(gridBagLayout)

        # Help Panel
        gridBagLayout = GridBagLayout()
        gridBagLayout.columnWidths = [ 0, 0 ]
        gridBagLayout.rowHeights = [ 10, 10 ]
        gridBagLayout.columnWeights = [ 0.0, 0 ]
        gridBagLayout.rowWeights = [0.0, 0 ]
        self._helpPanel = JPanel(BorderLayout())
        topLabel = JLabel()
        topLabel.setFont(Font("Lucida Grande", Font.BOLD, 18))
        #topLabel.setText("JWT Fuzzer usage:")
        topLabel.setText(helpText)

        c = GridBagConstraints()
        c.anchor = GridBagConstraints.FIRST_LINE_START
        c.fill = GridBagConstraints.NONE
        c.gridx = 0
        c.gridy = 0
        c.insets = Insets(0,10,0,10)
        self._helpPanel.add(topLabel,BorderLayout.PAGE_START)

        targetHelpHeaderLabel = JLabel()
        targetHelpHeaderLabel.setFont(Font("Lucida Grande", Font.BOLD, 14))
        targetHelpHeaderLabel.setText("Target Selection:")
        c = GridBagConstraints()
        c.anchor = GridBagConstraints.FIRST_LINE_START
        c.gridx = 0
        c.gridy = 1
        c.insets = Insets(0,10,0,10)
        #self._helpPanel.add(targetHelpHeaderLabel,BorderLayout.LINE_START)

        targetHelpLabel = JLabel()
        targetHelpLabel.setFont(Font("Lucida Grande", Font.PLAIN, 12))
        targetHelpLabel.setText(targetHelpText)
        c = GridBagConstraints()
        c.anchor = GridBagConstraints.FIRST_LINE_START
        c.insets = Insets(0,10,0,10)
        c.gridx = 0
        c.gridy = 2
        #self._helpPanel.add(targetHelpLabel,BorderLayout.PAGE_END)


        # Setup tabs
        self._tabs = JTabbedPane()
        self._tabs.addTab('Configuration',self._configurationPanel)
        self._tabs.addTab('Help',self._helpPanel)

        # Target Options
        targetLabel = JLabel("Target Selection (Required): ")
        targetLabel.setFont(Font("Tahoma",Font.BOLD, 12))
        c = GridBagConstraints()
        c.gridx = 0
        c.gridy = 1
        c.insets = Insets(0,10,0,0)
        c.anchor = GridBagConstraints.LINE_END
        self._configurationPanel.add(targetLabel,c)

        options = [ 'Header', 'Payload' ]
        self._targetComboBox = JComboBox(options)
        c = GridBagConstraints()
        c.gridx = 1
        c.gridy = 1
        c.anchor = GridBagConstraints.LINE_START
        self._configurationPanel.add(self._targetComboBox,c)


        # Selector Options
        selectorLabel = JLabel("JSON Selector (Required): ")
        selectorLabel.setFont(Font("Tahoma",Font.BOLD, 12))
        c = GridBagConstraints()
        c.gridx = 0
        c.gridy = 2
        c.insets = Insets(0,10,0,0)
        c.anchor = GridBagConstraints.LINE_END
        self._configurationPanel.add(selectorLabel, c)

        self._selectorTextField = JTextField('',80)
        c = GridBagConstraints()
        c.gridx = 1
        c.gridy = 2
        self._configurationPanel.add(self._selectorTextField, c)

        # Signature Options
        generateSignatureLabel = JLabel("Generate signature? (Required): ")
        generateSignatureLabel.setFont(Font("Tahoma",Font.BOLD, 12))
        c = GridBagConstraints()
        c.gridx = 0
        c.gridy = 3
        c.insets = Insets(0,10,0,0)
        c.anchor = GridBagConstraints.LINE_END
        self._configurationPanel.add(generateSignatureLabel,c)

        options = ["False", "True"]
        self._generateSignatureComboBox = JComboBox(options)
        c = GridBagConstraints()
        c.gridx = 1
        c.gridy = 3
        c.anchor = GridBagConstraints.LINE_START
        self._configurationPanel.add(self._generateSignatureComboBox,c)

        signatureAlgorithmLabel = JLabel("Signature Algorithm (Optional): ")
        signatureAlgorithmLabel.setFont(Font("Tahoma",Font.BOLD, 12))
        c = GridBagConstraints()
        c.gridx = 0
        c.gridy = 4
        c.insets = Insets(0,10,0,0)
        c.anchor = GridBagConstraints.LINE_END
        self._configurationPanel.add(signatureAlgorithmLabel,c)

        options = ["None","HS256","HS384","HS512","ES256","ES384","ES512","RS256","RS384","RS512","PS256","PS256","PS384","PS512"]
        self._algorithmSelectionComboBox = JComboBox(options)
        c = GridBagConstraints()
        c.gridx = 1
        c.gridy = 4
        c.anchor = GridBagConstraints.LINE_START
        self._configurationPanel.add(self._algorithmSelectionComboBox,c)

        signingKeyLabel = JLabel("Signing Key (Optional): ")
        signingKeyLabel.setFont(Font("Tahoma",Font.BOLD, 12))
        c = GridBagConstraints()
        c.gridx = 0
        c.gridy = 5
        c.insets = Insets(0,10,0,0)
        c.anchor = GridBagConstraints.LINE_END
        self._configurationPanel.add(signingKeyLabel,c)

        self._signingKeyTextArea = JTextArea()
        self._signingKeyTextArea.setColumns(50)
        self._signingKeyTextArea.setRows(10)
        signingKeyScrollPane = JScrollPane(self._signingKeyTextArea)
        c = GridBagConstraints()
        c.gridx = 1
        c.gridy = 5
        c.anchor = GridBagConstraints.LINE_START
        self._configurationPanel.add(signingKeyScrollPane,c)

        self._saveButton = JButton("Save Configuration", actionPerformed=self.saveOptions)
        c = GridBagConstraints()
        c.gridx = 1
        c.gridy = 6
        c.anchor = GridBagConstraints.FIRST_LINE_START
        self._configurationPanel.add(self._saveButton,c)

        
        callbacks.customizeUiComponent(self._configurationPanel)
        callbacks.customizeUiComponent(self._helpPanel)
        callbacks.customizeUiComponent(self._tabs)
        callbacks.addSuiteTab(self)
        print "test"
        return


    def getProcessorName(self):
        return "JWT Fuzzer"
    def processPayload(self, currentPayload, originalPayload, baseValue):
        dataParameter = self._helpers.bytesToString(
                         self._helpers.urlDecode(baseValue)
                       )
        
        header = jwt.get_unverified_header(dataParameter)
        payload = jwt.decode(dataParameter, verify=False)
        signature = dataParameter.split(".")[2] # Never decode this


        target = header if self._fuzzoptions["target"] == "Header" else payload
        selector = self._fuzzoptions["selector"]

        """
        Retrieve the value specified by the selector, 
        if this value does not exist, assume the user
        wants to add the value that would have been specified
        by the selector to the dictionary (this behavior will 
        be noted in the help docs)
        """
        try:
            value = self.getValue(target, selector)
        except:
            target = self.buildDict(target, selector)

        # Insert the intruder payload if the selector is valid
        if !isinstance(selector,type(None)):
            target = self.setValue(target, selector, self._helpers.bytesToString(currentPayload))

        # If the user wants to sign the data
        #   This WILL update the header algo

        modified_jwt = ""
        if self._fuzzoptions["signature"]:
            header["alg"] = self._fuzzoptions["algorithm"]
            modified_jwt = jwt.encode(
                    payload,
                    self._fuzzoptions["key"],
                    algorithm=self._fuzzoptions["algorithm"],
                    headers=header
                    )
        # Put the JWT back together
        else:
            encoded_header = self._helpers.base64Encode(
                                        self._helpers.stringToBytes(json.dumps(header))
                                    )
            encoded_payload = self._helpers.base64Encode(
                                        self._helpers.stringToBytes(json.dumps(payload))
                                    )

            encoded_header = encoded_header.replace('=','')
            encoded_payload = encoded_payload.replace('=','')

            encoded_header = self._helpers.urlEncode(encoded_header)
            encoded_payload = self._helpers.urlEncode(encoded_payload)
            
            modified_jwt = encoded_header + "." + encoded_payload + "." + signature

        print "Header: ",header
        print "Payload: ",payload
        print modified_jwt

        return self._helpers.stringToBytes(modified_jwt)

    #-----------------------
    # Helpers
    #-----------------------

    #-----------------------
    # getValue:
    #   @return: A value at arbitrary depth in dictionary
    #   @throws: TypeError
    #-----------------------
    def getValue(self, dictionary, values):
        return reduce(dict.__getitems__, values, dictionary)

    #-----------------------
    # buildDict:
    #   @note: Will build dictionary of arbitrary depth
    #-----------------------
    def buildDict(self, dictionary, keys):
        root = current = dictionary
        for key in keys:
            if key not in current:
                current[key] = {}
            current = current[key]
        return root

    #----------------------
    # setValue:
    #   @note: Will set key of arbitrary depth
    #-----------------------
    def setValue(self, dictionary, keys, value):
        root = current = dictionary
        for i,key in enumerate(keys):
            if i == len(keys) - 1:
                current[key] = value
                break
            if key in current:
                current = current[key]
            else:
                # Should never happen
                current = self.buildDict(current, keys)
        return root
    
    #-----------------------
    # End Helpers
    #-----------------------

    #-----------------------
    # Implement ITab
    #-----------------------

    def getTabCaption(self):
        return "JWT Fuzzer"

    def getUiComponent(self):
        return self._tabs

    #---------------------------
    # Save configuration options
    #---------------------------

    def saveOptions(self,event):
        print "Saving!"
        self._fuzzoptions["target"]     = self._targetComboBox.getSelectedItem()
        self._fuzzoptions["selector"]   = self._selectorTextField.getText()
        self._fuzzoptions["signature"]  = True if self._generateSignatureComboBox.getSelectedItem() == "True" else False
        self._fuzzoptions["algorithm"]  = self._algorithmSelectionComboBox.getSelectedItem()
        self._fuzzoptions["key"]        = self._signingKeyTextArea.getText()

        # Sanity check selector
        m = re.search("(\.\w+)+",self._fuzzoptions["selector"])
        if isinstance(m,type(None)) or m.group(0) != self._fuzzoptions["selector"]:
            self._saveButton.setText("Invalid selector!")
        else:
            self._fuzzoptions["selector"] = self._fuzzoptions["selector"].split(".")[1:]
            print "Selector: ",self._fuzzoptions["selector"]
            self._saveButton.setText("Save Configuration")
        return

helpText = """<html>
<p style="font-size:18px"><b>JWT Fuzzer Help: </b></p><br />
<p style="font-size:14px"><i>Target Selection: </i></p><br />
<p style="font-size:12px">Select which section of the JWT you will be fuzzing.
<br />You can fuzz the <b>"Header"</b> section or the <b>"Payload"</b> section
This will default to the <b>"Header"</b> section</p><br />
<p style="font-size:14px"><i>Selector: </i></p><br />
<p style="font-size:12px">Specify a selector for the value you wish to fuzz. This is done using <a href="https://stedolan.github.io/jq/manual/">jq's Object Identifier-Index</a> syntax. <br />
<i>Example 1: </i> Fuzzing the "alg" value<br /> 
If you wished to fuzz the value of "alg" you would specify </b>Header</b> as your target and use <i>.alg</i> as your selector. <br />
<i>Example 2: </i> Fuzzing nested values <br />
Say you JWT payload had a claim that looked like this: <br />
<i>{</i> <br />
<i>   "user" : { </i> <br />
<i>       "username" : "john.doe", </i> <br />
<i>       "role" : "admin" </i> <br />
<i>    } </i> <br />
<i>}</i><br /><br />
To fuzz the <i>role</i>, your selector would be <i>.user.role</i> and your target would be <b>Payload</b><br />
</html>"""
targetHelpText = """<html><p style="font-size:20px">Selection which section of the JWT will be fuzzed.<br />You can fuzz the <b>"Header"</b> section or the <b>"Payload"</b> section</p></html>"""




