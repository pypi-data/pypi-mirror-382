from typing import Optional

from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType
from pyspark.sql.column import Column
from pyspark.sql.functions import lit


class UDFBase:
    sparkSession = None
    UDFUtils = None

    def __init__(self, spark):
        self.UDFUtils = spark.sparkContext._jvm.io.prophecy.libs.python.UDFUtils
        self.sparkSession = spark


udfConfig: Optional[UDFBase] = None


def initializeUDFBase(spark):
    global udfConfig
    if udfConfig is None:
        udfConfig = UDFBase(spark)
    return udfConfig


def rest_api(*cols):
    _cols = udfConfig.sparkSession.sparkContext._jvm.PythonUtils.toList(
        [item._jc for item in list(cols)]
    )
    rest_api_response = udfConfig.UDFUtils.rest_api(_cols)
    return 1


def call_udf(udfName: str, *cols):
    """
    Cross-version UDF caller that avoids private _to_java_column/_to_seq.
    Accepts Column or Python literals.
    """
    sc = udfConfig.sparkSession.sparkContext

    jcols = []
    for c in cols:
        # Accept Column or anything exposing a _jc (Java Column)
        if not hasattr(c, "_jc"):
            c = lit(c)
        jcols.append(c._jc)

    jseq = sc._jvm.PythonUtils.toSeq(jcols)
    jcol = udfConfig.UDFUtils.call_udf(udfName, jseq)
    return Column(jcol)
