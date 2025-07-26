the docker container deenihl/ollama-medcpt contains an ollama service and locally registered ollama model oscardp96/medcpt-article. you should be able to connect to it and make embedding requests. either using the openai compatible embedding endpoint or using the ollama client

e.g.
curl http://localhost:11434/api/embed -d '{
  "model": "oscardp96/medcpt-article",
  "input": "Llamas are members of the camelid family"
}'
or 

ollama.embed({
    model: 'oscardp96/medcpt-article',
    input: 'Llamas are members of the camelid family',
})

when embedding LOINCs into qdrant you should include the following payload properties
Fully-Specified Name
LOINC code
Component
Property 
Time
System
Scale
Method

these are the various parts of a loinc code
property : The kind of property distinguishes between different kinds of quantities of the same substance. Analytes are often measured using different types of units. Kinds of properties include: Mass, Substance, Catalytic Activity, Arbitrary, and Number. Pharmaceutical industry terms for tests include properties, such as Mass Substance Concentration (MSCnc) or Mass Substance Rate (MSRat). Definitions for the main property categories may be found in LOINC Users' Guide.

Each of the properties also has subtypes including: concentration (amount divided by a volume like mg/dl or gm/L), contents (amount divided by a mass like umol/ g creatinine), ratios (one measure divided by another taken from the same system), fractions (ratios of a part over a whole, usually reported as a percent), and rates [a measure taken over time like mg/day (a mass rate=MRat) or a clearance volume rate (expressed as a clearance=VRAT)]. For more information, refer to the Kind of Property (2nd Part) section of the LOINC Users' Guide.
Time Aspect: A measurement may be taken at a moment in time or measured over a specified time interval. For more information, refer to Time Aspect (Point or moment in time vs. time interval) (3rd part) section of the LOINC Users' Guide.
System: A system may consist of up to two parts.

The first part names the system, and
the second part names a subpart of the sample that is not the patients (e.g., fetus, donor, blood product unit, etc.).
Chemistry tests are usually run on serum, urine, blood and/or cerebrospinal fluid (CSF). The code "XXX" is used to identify a material that is not specified in another part of the HL7 message (e.g., OBX specimen segment). When testing on serum or plasma is clinically equivalent, the system "Ser/Plas" should be used.

If the test is run on a combination of types of systems (such as the ration of substance found in CSF and plasma) the codes are joined with a "+" such as PLAS+CSF.

In cases where super systems apply, the subpart will be delimited with a "^" such as A AG:ACNC:PT:RBC:^BPU:ORD which specifies the A Antigen reported on a blood product pack assigned to that patient. Refer to System (Sample) Type (4th part) section of the LOINC Users' Guide.

Scale: Type of scale specifies the scale of the measure. The following scale types are defined: Quantitative(Qn), Ordinal(Ord), Nominal(Nom), Narrative(Nar). For more information, refer to Type of Scale (5th part) section of the LOINC Users' Guide.

Method: ype of method specifies the method used to perform the test. The method axis is an optional component of a fully-specified LOINC name. It is only used when the information in the other axes does not sufficiently distinguish clinical measurements that have very different reference ranges, sensitivities, or specificities. In general, a method is specified when clinicians would want to see observations made by one particular method separated from measurements made by a different methodology when displayed in a clinical report. For the purpose of data exchange and further specificity, the reference range and method can also be sent in other fields of ASTM, HL7, and CEN TC251 result messages. For more information, refer to Type of Method (6th part) section of the LOINC Users' Guide.