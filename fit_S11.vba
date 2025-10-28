Sub Main () 

    Dim projectPath As String
    Dim pythonExe As String
    Dim pythonScript As String
    Dim resultFile As String
    Dim fso As Object
    Dim file As Object
    Dim jsonText As String
    Dim key As String
    Dim Qi As Double, Qc As Double, Ql As Double, fr As Double
    Dim objShell As Object
    Dim RetVal As Integer
    Dim pythonCmd As String
    Dim resultQi As Object, resultQc As Object, resultQl As Object, resultFr As Object

    projectPath = GetProjectPath("Project")
    pythonExe = "C:\Program Files (x86)\CST Studio Suite 2025\AMD64\python\python.bat"
    pythonScript = "C:\Program Files (x86)\CST Studio Suite 2025\Library\Python\scripts\CST_fit_S11.py"
    resultFile = projectPath & "\fit_results_temp.json"
	pythonCmd = """" & pythonExe & """ """ & pythonScript & """"

    Set objShell = CreateObject("WScript.Shell")
    RetVal = objShell.Run(pythonCmd, 0, True) ' Run and wait for S11 fit
    If RetVal Then ' fitting script errored
        fr = -1
        Qi = -1
        Qc = -1
        Ql = -1
    Else
        ' Read the JSON file
        Set fso = CreateObject("Scripting.FileSystemObject")
        If fso.FileExists(resultFile) Then
            Set file = fso.OpenTextFile(resultFile, 1)
            jsonText = file.ReadAll
            file.Close
        End If

        ' Very crude parsing (since VBA doesn’t have JSON natively)
        On Error Resume Next
        fr = CDbl(Split(Split(jsonText, """fr"": ")(1), ",")(0))
        Qi = CDbl(Split(Split(jsonText, """Qi"": ")(1), ",")(0))
        Qc = CDbl(Split(Split(jsonText, """Qc"": ")(1), ",")(0))
        Ql = CDbl(Split(Split(jsonText, """Ql"": ")(1), ",")(0))
    End If



    ' MsgBox "Completed S11 fit:\nfr = " & fr & " GHz" & vbNewLine & "Qi = " & Qi & vbNewLine & "Qc = " & Qc & vbNewLine & "Ql = " & Ql,

    ' Store as results
    Set resultFr = Result0D("")
    Set resultQi = Result0D("")
    Set resultQc = Result0D("")
    Set resultQl = Result0D("")

    With resultFr
    	.SetData(fr)
    	.Title("Resonant Frequency")
    	.SetDataLabelAndUnit("frequency", "GHz")
    	.SetFileName("resonant_frequency")
    	.Save()
    	.AddToTree("S11 fit\fr")
    End With

    With resultQi
    	.SetData(Qi)
    	.Title("Internal Quality Factor")
    	.SetDataLabelAndUnit("quality", "")
    	.SetFileName("internal_quality")
    	.Save()
    	.AddToTree("S11 fit\Qi")
    End With

    With resultQc
    	.SetData(Qc)
    	.Title("External Quality Factor")
    	.SetDataLabelAndUnit("quality", "")
    	.SetFileName("external_quality")
    	.Save()
    	.AddToTree("S11 fit\Qc")
    End With

    With resultQl
    	.SetData(Ql)
    	.Title("Loaded Quality Factor")
    	.SetDataLabelAndUnit("quality", "")
    	.SetFileName("loaded_quality")
    	.Save()
    	.AddToTree("S11 fit\Ql")
    End With

End Sub